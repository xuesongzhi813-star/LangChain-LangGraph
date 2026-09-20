
'''工作流模式：提示链模式'''
import os
from typing import TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START
from langgraph.graph import StateGraph

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#定义输入状态
class InputState(TypedDict):
    topic:str

#定义输出状态
class OutputState(TypedDict):
    artical:str

#定义中间状态(完整+内部使用)
class State(InputState,OutputState):
    outline: str  # 第⼀步：⽣成的⼤纲
    draft: str  # 第⼆步：⽣成的初稿
    polished_draft: str  # 第三步：润⾊后的稿件

#定义节点-->生成大纲
PROMPT_1 = (
"根据主题⽣成⽂章⼤纲。\n"
"主题：{topic}\n"
"要求："
"1.只需两个最核⼼标题"
"2.不⽤进⾏说明，只返回最终⼤纲"
)
def node_1(
        state:InputState
)->State:
    print("*" * 50)
    print("正在根据主题生成大纲")
    prompt=PROMPT_1.format(topic=state["topic"])
    response=model.invoke([HumanMessage(content=prompt)])
    print(f"大纲已生成:\n{response}\n")
    return {
        "outline":response,
        "topic":state["topic"] #子类继承父类顺带的属性
    }

#定义节点-->生成初稿
PROMPT_2 = (
"根据以下内容⽣成⽂章完整初稿。\n"
"主题：{topic}\n"
"⼤纲: "
"{outline}\n"
"要求："
"1.每个标题下，最多使⽤三句话的内容即可"
"2.不⽤进⾏说明，只返回最终结果"
)
def node_2(
        state:State
):
    print("*" * 50)
    print("正在根据主题生成初稿")
    prompt = PROMPT_2.format(topic=state["topic"],outline=state["outline"])
    response = model.invoke([HumanMessage(content=prompt)])
    print(f"初稿已生成:\n{response}\n")
    return {
        "draft":response,
    }

#定义节点-->润色初稿
PROMPT_3 = (
"根据⽂章初稿进⾏润⾊。\n"
"主题：{topic}\n"
"初稿: "
"{draft}\n"
"要求："
"1.润⾊后，⽂章不能太⻓"
)
def node_3(
        state:State
):
    print("*" * 50)
    print("正在对初稿进行润色")
    prompt = PROMPT_3.format(topic=state["topic"], draft=state["draft"])
    response = model.invoke([HumanMessage(content=prompt)])
    print(f"润色初稿后正文:\n{response}\n")
    return {
        "polished_draft":response,
    }

#定义节点-->生成最终版本文章
PROMPT_4 = (
"根据润⾊版⽂章，⽣成⽂章终稿。\n"
"主题：{topic}\n"
"⼤纲: "
"{outline}\n"
"润⾊版⽂章: "
"{polished_draft}\n"
)
def node_4(
        state:State
):
    print("*" * 50)
    print("正在生成最终版")
    prompt = PROMPT_4.format(topic=state["topic"], outline=state["outline"], polished_draft=state["polished_draft"])
    response = model.invoke([HumanMessage(content=prompt)])
    print(f"最终文章:\n{response}\n")
    return {
        "artical":response, #继承父类顺带的属性
    }

#定义图，添加节点，添加边
builder=StateGraph(State,input_schema=InputState,output_schema=OutputState)
builder.add_sequence([node_1,node_2,node_3,node_4])
builder.add_edge(START,"node_1")

graph=builder.compile()

result=graph.invoke(
    {"topic":"AI关于就业的影响"}
)
print(result)
