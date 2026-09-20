'''协调者-工作者模式:
不同于“并行化模式”，具体的任务问题，要由“协调者”分配
'''
import operator
import os
from typing import TypedDict, Annotated

from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field


#定义状态
class State(TypedDict):
    topic: str #任务主题
    sections:list #任务清单，拆分好的
    completed_sections: Annotated[list[str],operator.add] #任务结果清单
    final_report:str #整合最终结果

#定义任务格式
class Section(BaseModel):
    name: str
    description: str

class section(BaseModel):
    section_list: list[Section]

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
extra_body={"thinking": {"type": "disabled"}} #关闭思考模式
)

planner=model.with_structured_output(section,method="function_calling") #DeepSeek不支持json_schema方式，必须用function_calling

#定义节点
# 协调者节点 - 制定计划
def orchestrator(state: State):
    """协调者：分析任务并制定执⾏计划"""
    report_sections = planner.invoke(
        f"为主题'{state['topic']}'制定报告⼤纲，包含3个章节"
    )
    return {"sections": report_sections.section_list}

# ⼯作者节点 - 执⾏具体任务
def llm_call(state: State):
    """⼯作者：根据分配的任务⽣成内容"""
    section = state["section"]  # 从协调者接收的任务
    result = model.invoke(
        f"编写报告章节：{section.name}，内容要求：{section.description}"
    )
    return {"completed_sections": [result.content]}  # 结果会⾃动合并

# 汇总节点
def synthesizer(state: State):
    """汇总所有⼯作者的成果"""
    completed_sections = state["completed_sections"]
    final_report = "\n\n---\n\n".join(completed_sections)
    return {"final_report": final_report}

# 任务分配函数 - 关键部分！
def assign_workers(state: State):
    """为每个任务创建⼯作者"""
    # 为每个章节创建⼀个⼯作者任务
    worker_tasks = []
    for section in state["sections"]:
        worker_tasks.append(
            Send("llm_call", {"section": section})  # 发送任务给⼯作者
        )
    return worker_tasks

# 构建⼯作流
builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("llm_call", llm_call)
builder.add_node("synthesizer", synthesizer)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges(
"orchestrator",
assign_workers,
["llm_call"] # 创建的⼯作者都指向llm_call节点
)
# 所有⼯作者完成后汇总
builder.add_edge("llm_call", "synthesizer")
builder.add_edge("synthesizer", END)
worker = builder.compile()
response =worker.invoke({"topic": "中国近代史"})
print(response)




