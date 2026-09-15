import os

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def create_calendar_event(
title: str,
start_time: str, # ISO⽇期时间格式, 如: "2000-01-15T14:00:00"
end_time: str, # ISO⽇期时间格式, 如: "2000-01-15T15:00:00"
attendees: list[str], # 参与者: email 地址列表
location: str = ""
) -> str:
    """创建⼀个⽇程事件。需要使⽤精确的 ISO ⽇期时间格式。"""
    # 说明：实际上，这会调⽤⾕歌⽇历 API、Outlook API 等相关服务。
    return f"活动创建：{title}，从 {start_time} ⾄ {end_time}，参与⼈数为{len(attendees)} ⼈。"


@tool
def get_available_time_slots(
attendees: list[str], # 参与者: email 地址列表
date: str, # 格式: "2024-01-15"
duration_minutes: int # 持续时间（分钟）
) -> list[str]:
    """查询特定⽇期内给定参会者的可⽤时间段，其他时间不可⽤。"""
    # 说明：实际上，这将调⽤⽇历服务的 API 来进⾏查询。
    return ["09:00-10:00", "14:00-15:00", "16:00-18:00"]

CALENDAR_AGENT_PROMPT = (
"你是⼀个⽇历⽇程安排助⼿。"
"将⾃然语⾔的⽇程请求（例如“下周⼆下午2点”）解析为符合规范的ISO⽇期时间格式。"
"必要时使⽤ get_available_time_slots 检查可⽤时间段。"
"如果没有合适的时间段，请停⽌并在回复中确认⽆法安排。"
"使⽤ create_calendar_event 来安排⽇程。"
"在最终回复中务必确认已安排的内容。"
)

#定义agent
model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

calendar_agent=create_agent(
    model=model,
    system_prompt=CALENDAR_AGENT_PROMPT,
    tools=[create_calendar_event,get_available_time_slots],
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={"create_calendar_event":True},
        description_prefix="等待创建日程安排的审批……"
    )]
)

# #测试agent（采取“流式输出”更好观察结果）
# for chunk in calendar_agent.stream(
#     {"messages":[{"role":"user","content":"我想在2026-9-18下午3点钟，开一个1小时的商讨会议"}]}
# ):
#     for item in chunk.values():
#         for message in item.get("messages",[]):
#             message.pretty_print()