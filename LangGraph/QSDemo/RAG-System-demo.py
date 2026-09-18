#实现一个自己的RAG流程
#1.构建知识库
#（1）定义“文档加载器”
import os
from typing import Literal

from langchain_core.messages import HumanMessage, convert_to_messages, filter_messages
from langchain_core.tools import create_retriever_tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field

#以脚本所在目录为基准解析相对路径（这样无论从哪个工作目录运行都能找到Docs）
script_dir=os.path.dirname(os.path.abspath(__file__))
paths=[
    "../Docs/C++开发方向.md",
    "../Docs/Java开发方向.md",
    "../Docs/企业介绍.md",
    "../Docs/测试开发方向.md",
]
#UnstructuredMarkdownLoader只接受单个文件路径，需要逐个加载后合并
docs=[]
for p in paths:
    loader=UnstructuredMarkdownLoader(file_path=os.path.join(script_dir,p))
    docs.extend(loader.load())

#（2）定义“文本分割器”
splitter=CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=400,
    chunk_overlap=30,
)
documents=splitter.split_documents(docs)

#（3）定义“嵌入模型”
#定义嵌入模型
embeddings = OpenAIEmbeddings(
    model="BAAI/bge-m3",  # 免费模型，中英文效果都好
    base_url="https://api.siliconflow.cn/v1",
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    check_embedding_ctx_length=False,  # bge-m3不需要token计数，关闭可避免多余请求
)

#(4)定义向量数据库
vector_store=InMemoryVectorStore.from_documents(
    embedding=embeddings,  #注意参数名是embedding而不是embeddings
    documents=documents,
)

#(5)使用LangChain的预构建 create_retriever_tool 创建检索工具
retriever=vector_store.as_retriever(search_kwargs={"k": 2})
retriever_tool=create_retriever_tool(
    retriever,
    "retriever_bit",
    "搜索并返回有关比特就业课的信息"
)


#定义模型
model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

#1.定义状态
#直接使用LangGraph封装好的历史消息列表

#2.定义节点
#节点1：定义LLM+绑定了工具-->初步执行结果的节点
def generate_query_or_response(
        state:MessagesState
):
    '''判断问题需要调用工具解决/直接回答'''
    response=model.bind_tools([retriever_tool]).invoke(state["messages"])
    return {
        "messages":[response]
    }
#测试节点1
# generate_query_or_response(
#     {"messages":[HumanMessage(content="介绍一下比特就业课基本情况")]}
# )["messages"][-1].pretty_print()


#节点2：检索器节点（检索器工具执行，依据AIMessage中是否有tool_calls）-->通过LangGraph封装成一个节点
retriever_node=ToolNode([retriever_tool])
# #测试节点2
# input_messages = {
# "messages": convert_to_messages([{
# "role": "user",
# "content": "⽐特提供了哪些课程?",
# },
# {
# "role": "assistant",
# "content": "",
# "tool_calls": [{
# "id": "1",
# "name": "retrieve_bit",
# "args": {"query": "⽐特课程"},
# }],},
# {"role": "tool", "content": "你好", "tool_call_id": "1"},
# ])}
# retriever_node(input_messages)["messages"][-1].pretty_print()


REWRITE_PROMPT = (
"查看输⼊并尝试推断潜在的语义意图/含义。\n"
"这是最初的问题："
"\n ------- \n"
"{question}"
"\n ------- \n"
"提出⼀个改进后的问题："
)
#节点3：重写问题节点
def rewrite_question_node(
  state:MessagesState
):
    '''检索结果不理想，重新调用LLM
    并且结合提示词模板，重构用户问题，构建成HumanMessage重发给LLM
    并且追加到历史消息列表
    '''
    #获取用户问题（注意取.content，否则整个消息对象的repr会被拼进提示词）
    question=state["messages"][0].content
    #实例化提示词模板+构建HumanMessage
    re_question=REWRITE_PROMPT.format(question=question)
    result=model.invoke([HumanMessage(content=re_question)])
    return {
        "messages":[{"role":"user","content":result.content}]
    }


# ⽣成答案
GENERATE_PROMPT = (
"你是负责回答问题的助⼿。 "
"使⽤以下检索到的上下⽂⽚段来回答问题。 "
"如果你不知道答案，就说你不知道。 "
"最多只⽤三句话，回答要简明扼要。\n"
"Question: {question} \n"
"Context: {context}"
)
#节点4：根据历史消息，生成答案
def generate_answer(
        state:MessagesState
):
    '''
    根据“用户初始问题”+“最终检索结果”-->LLM整合生成答案
    '''
    question=state["messages"][0].content
    context=state["messages"][-1].content
    #整合成HumanMessage发给LLM
    prompt=GENERATE_PROMPT.format(question=question,context=context)
    result=model.invoke([HumanMessage(content=prompt)])
    return {
        "messages":[result]
    }

#3.定义图
RAG_system=StateGraph(MessagesState)

#4.添加节点
RAG_system.add_node("generate_query_or_response",generate_query_or_response)
RAG_system.add_node("retriever_node",retriever_node)
RAG_system.add_node("rewrite_question_node",rewrite_question_node)
RAG_system.add_node("generate_answer",generate_answer)

#5.添加边
RAG_system.add_edge(START,"generate_query_or_response")
#定义根据AIMessage中是否有tool_call来判断调用工具
RAG_system.add_conditional_edges("generate_query_or_response",tools_condition,
                                 {
                                     "tools":"retriever_node",
                                     "__end__":END
                                 })


#定义判断Tool调用生成结果是否能解决用户问题
GRADE_PROMPT = (
"你是⼀个评分员，评估检索到的⽂档与⽤⼾问题的相关性。 \n "
"以下是检索到的⽂档： \n\n {context} \n\n"
"以下是⽤⼾的问题： {question} \n"
"如果⽂档包含与⽤⼾问题相关的关键字或语义，则将其评为相关。 \n"
"给出⼀个⼆元分数“yes”或“no”，以表明该⽂档是否与问题相关。"
)
class OutputResult(BaseModel):
    result:str=Field(description="只能输出“yes”or“no”，相关则为yes，不相关则为no")

def Review_Context(state:MessagesState)->Literal["rewrite_question_node","generate_answer"]:
    '''
    将ToolMessage中内容+提示词-->LLM判断相关性-->根据结果，决定跳转节点
    '''
    #获取到ToolMessage中内容
    context=state["messages"][-1].content
    #获取用户最初问题
    question=state["messages"][0].content
    #实例化“提示词模板”
    prompt=GRADE_PROMPT.format(context=context,question=question)
    #发送给LLM判断相关性
    #注意1：模型输入必须是消息列表/字符串，裸字典和单个消息对象都会被_convert_input拒绝
    #注意2：DeepSeek不支持默认的json_schema响应格式，需改用function_calling方式
    #注意3：deepseek-flash默认开启思考模式，而思考模式不支持强制tool_choice，
    #       因此本次调用需要通过extra_body临时关闭思考模式
    response=model.with_structured_output(
        OutputResult,
        method="function_calling"
    ).invoke(
        [HumanMessage(content=prompt)],
        extra_body={"thinking": {"type": "disabled"}}
    )
    response=response.result
    if response=="yes":
        return "generate_answer"
    else:
        return "rewrite_question_node"

RAG_system.add_conditional_edges("retriever_node",Review_Context,["generate_answer","rewrite_question_node"])

RAG_system.add_edge("rewrite_question_node","generate_query_or_response")
RAG_system.add_edge("generate_answer",END)

#编译+测试
RAG_system=RAG_system.compile()

for chunk in RAG_system.stream(
    {"messages":[{"role":"user","content":"关于比特的基本信息"}]}
):
    print(chunk)

