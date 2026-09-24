import operator
import os
import uuid
from typing import Optional, TypedDict, Annotated

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore #注意：不能用langchain_core.stores里的InMemoryStore（那是retriever的docstore，没有put/search）
from pydantic import Field, BaseModel

'''
Store在LangGraph中的使用:不同线程会话，借助持久性会话完成喜好推荐（跨线程记忆）
基于“快速上手”2搜索助手
'''

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    extra_body={"thinking": {"type": "disabled"}}
)

search_tool=TavilySearch(max_results=3)

with_tools_model=model.bind_tools([search_tool])

#设置LLM在“会话”中需要保存的信息，通过类输出并且保存-->只保存有用的数据
class Person(BaseModel):
    name:Optional[str]=Field(description="一个人的名字")
    height:Optional[float]=Field(description="一个人的身高，以米为单位")
    favorite_food:Optional[str]=Field(description="一个人最爱吃的食物")

config1={"configurable":{"thread_id":"1","user_id":"111"}}
config2={"configurable":{"thread_id":"2","user_id":"111"}}

#定义状态
class MessageState(TypedDict):
    messages:Annotated[list[str],operator.add]
    llm_calls:int


#定义节点
'''注意事项：在LangGraph中使用store，节点新添的参数：状态+线程（RunnableConfig）+store（BaseStore）'''
def store_node(state:MessageState,config:RunnableConfig,store:BaseStore):
    '''通过LLM提取用户信息'''

    #1.先提取用户信息（按照结构化输出）
    user_info=model.with_structured_output(Person,method="function_calling").invoke(
        [SystemMessage(
            content="你是一个信息提取专家，只从文本中提取我的相关信息，不能提取别人的信息"
                    "如果你不知道要提取属性的值，属性值可以返回null"
        )]
        +state["messages"][-3:]  #查看最近三条消息-->从与用户的会话中提取（列表拼接）
    )

    #2.保存
    user_id=config["configurable"]["user_id"]

    #保存用户基本信息-->通过namespace隔绝，memory_id+value定位+存储
    namespace1=(user_id,"info")

    #先存储用户相关信息
    store.put(
        namespace1,
        str(uuid.uuid4()), #memory_id
        {
            "name":user_info.name,
            "height":user_info.height,
        } #value通过字典形式存储
    )

    #再存储用户喜欢的食物
    namespace2=(user_id,"favorite_food")
    store.put(
        namespace2,
        str(uuid.uuid4()),
        {
            "favorite_food":user_info.favorite_food,
        }
    )

    #因为使用LLM提取信息，llm调用次数+1
    return {
        "llm_calls":state.get("llm_calls",0)+1,
    }

def llm_call_node(state:MessageState,config:RunnableConfig,store:BaseStore):
    '''判断问题是否需要调用工具的节点'''
    #先通过user_id查询历史信息中，是否有用户相关信息
    user_id=config["configurable"]["user_id"]
    namespace1=(user_id,"info")
    namespace2=(user_id,"favorite_food")

    info_result=store.search(namespace1)
    food_result=store.search(namespace2)

    return{
        "messages":[
            with_tools_model.invoke(
                [
                    SystemMessage(
                        content=f"你是⼀个乐于助⼈的助⼿，⽀持调⽤⼯具进⾏搜索。"
                                f"查询 LLM 前可参考以下信息："
                                f"1. ⽤⼾基本情况：{info_result[0].value} "
                                f"2. ⽤⼾偏好情况：{food_result[0].value}"
                    )
                ]+state["messages"]
            )
        ],
        "llm_calls":state.get("llm_calls",0)+1,
    }

search_node=ToolNode([search_tool])

#定义图，添加点，添加边
builder=StateGraph(MessageState)

builder.add_node(store_node)
builder.add_node(llm_call_node)
builder.add_node("search_node",search_node) #ToolNode实例需显式指定节点名，否则默认注册为"tools"

builder.add_edge(START,"store_node")
builder.add_edge("store_node","llm_call_node")
builder.add_conditional_edges("llm_call_node",tools_condition,
                              {
                                  "tools":"search_node",
                                  "__end__":END
                              })

#涉及线程，还要加入线程级持久化
checkpointer=InMemorySaver()
store=InMemoryStore()

graph=builder.compile(checkpointer=checkpointer,store=store)

result1=graph.invoke({"messages":[HumanMessage(content="我叫小明，身高1.8，最喜欢吃西冷牛排，我们朋友小红喜欢吃红烧肉")]},
                     config1)
print(f"总共调用llm次数:{result1["llm_calls"]}")
for item in result1["messages"]:
    item.pretty_print()

result2=graph.invoke({"messages":[HumanMessage(content="帮我推荐几家餐厅")]},config2)
print(f"总共调用llm次数:{result2["llm_calls"]}")
for item in result2["messages"]:
    item.pretty_print()
