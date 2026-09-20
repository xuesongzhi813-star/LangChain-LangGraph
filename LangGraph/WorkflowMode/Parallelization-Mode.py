'''并行化模式：多个问题互相独立，同时进行(预先定义好了子任务)
-->适合：“多维度”对一个问题进行分析处理（因为是多维度，大家都要进行+同时进行，用不上条件边）
'''
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph


#定义状态
class State(TypedDict):
    concept: str  # 概念
    market: str  # 市场分析
    competitor: str  # 竞品分析
    tech: str  # 技术分析
    report: str  # 汇总报告

#定义节点
def market_node(
        state:State
):
    '''负责“市场分析”的节点'''
    print("正在进行市场分析...")
    return {
        "market":"⽤⼾关注续航、重量、防盗，对骑⾏社交有兴趣..."
    }

def competitor_node(
        state:State
):
    '''负责“竞争分析”的节点'''
    print("正在进行竞争分析...")
    return {
        "competitor":"传统品牌智能化不⾜，互联⽹品牌续航和售后差..."
    }

def tech_node(
        state:State
):
    '''负责“技术分析”的节点'''
    print("正在进行技术分析...")
    return {
        "tech":"轻量化电池⻋⾝、GPS防盗、社交App集成..."
    }

def report_node(
        state:State
):
    '''负责“汇总报告”的节点'''
    print("正在进行汇总报告...")
    report = f"产品分析报告\n\n"
    report += f"市场分析：\n{state['market']}\n\n"
    report += f"竞品分析：\n{state['competitor']}\n\n"
    report += f"技术分析：\n{state['tech']}\n\n"
    report += "建议：聚焦续航、防盗、社交功能的平衡发展"
    return {
        "report":report
    }

#定义图，添加节点，添加边
builder=StateGraph(State)

builder.add_node(market_node)
builder.add_node(competitor_node)
builder.add_node(tech_node)
builder.add_node(report_node)

builder.add_edge(START,"market_node")
builder.add_edge(START,"competitor_node")
builder.add_edge(START,"tech_node")
builder.add_edge("market_node","report_node")
builder.add_edge("competitor_node","report_node")
builder.add_edge("tech_node","report_node")
builder.add_edge("report_node",END)

graph=builder.compile()
result=graph.invoke({"concept":"帮我做关于智能电动车的调研"})
print(result["report"])


