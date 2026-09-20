'''路由模式：任务分析器，分析问题类型-->分配给处理不同问题的节点（适用于：专业化处理）'''
import os
from typing import TypedDict, Literal

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    extra_body={"thinking": {"type": "disabled"}} #关闭思考模式
)

#定义状态
class InputState(TypedDict):
    input:str

class OutputState(TypedDict):
    output:str

class State(InputState, OutputState):
    decision:str

#定义节点
#问题分析器节点
# 定义路由决策的数据结构
class Route(BaseModel):
    step: Literal["pre_sale", "after_sale", "technical"] = Field(
        description="根据⽤⼾问题类型决定路由到售前、售后还是技术处理"
    )

def Problem_Analyzer(
        state:InputState
)->State:
    '''分析问题类型，并且分配给对应节点'''
    response=(model.with_structured_output(Route,method="function_calling")
              .invoke([HumanMessage(content=state["input"])]))
    return {
        "decision":response.step,
    }

#售前处理节点
def pre_sale(
        state:State
):
    '''售前处理'''
    print("正在进行售前处理...")
    return {
        "output":"售前处理工作完成"
    }

def after_sale(
        state:State
):
    '''售后处理'''
    print("正在进行售后处理...")
    return {
        "output":"售后处理工作完成"
    }

def technical(
        state:State
):
    '''技术处理'''
    print("正在进行技术处理...")
    return {
        "output":"技术工作完成"
    }

#定义图，添加节点，添加边
builder=StateGraph(State,input_schema=InputState,output_schema=OutputState)

builder.add_node(Problem_Analyzer)
builder.add_node(pre_sale)
builder.add_node(after_sale)
builder.add_node(technical)

builder.add_edge(START,"Problem_Analyzer")

def select_node(
        state:State
):
    '''添加边，根据decision的结果选择下一个传递的节点'''
    decision=state["decision"]
    if decision=="pre_sale":
        return "pre_sale"
    elif decision=="after_sale":
        return "after_sale"
    elif decision=="technical":
        return "technical"
    else:
        '''默认返回pre_sale'''
        return "pre_sale"

builder.add_conditional_edges("Problem_Analyzer",select_node,["pre_sale","after_sale","technical"])
builder.add_edge("pre_sale",END)
builder.add_edge("after_sale",END)
builder.add_edge("technical",END)

graph=builder.compile()

# 测试
test_cases = [
"我想了解⼀下你们产品的价格和功能", # 售前咨询
"我购买的产品有质量问题，需要退货", # 售后问题
"这个软件安装后⽆法正常运⾏，报错代码0x80070005", # 技术问题
"请问你们的售后服务政策是什么", # 售前咨询
"我的订单已经发货但还没收到", # 售后问题
"如何配置数据库连接参数" # 技术问题
]
for test_case in test_cases:
    print("*" * 50)
    result = graph.invoke({"input": test_case})
    print(f"⽤⼾问题：{test_case}\n{result['output']}")



