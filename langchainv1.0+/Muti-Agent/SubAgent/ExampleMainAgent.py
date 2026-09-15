import json
import os

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command

import ExampleCalendarAgent
import ExampleEmailAgent

#在本文件项目中，实现“控制信息流”的功能
#在封装的Agent中添加runtime上下文即可

#封装agent为工具
@tool
def shcedule_calendar(request:str,runtime:ToolRuntime)->str:
    '''
    专门负责安排时间相关的工具
    当任务涉及“查询空闲时间”+“安排日程事件”时，可以调用此工具完成需求
    '''
    #添加可以上下文
    # history_message=next(
    #     message for message in runtime.state["messages"] if message.type ==
    #     "human"
    # )
    #
    # prompt=[
    #     "你正在帮助用户解决问题的场景下\n\n"
    #     f"{history_message}\n"
    #     "接下来传入的新问题是，继续在该任务场景下解决问题\n\n"
    #     f"{request}"
    # ]
    result=ExampleCalendarAgent.calendar_agent.invoke(
        {"messages":[{"role":"user","content":request}]}
    )
    #json.dumps 返回 JSON 字符串（工具必须返回 str）；
    #json.dump(obj, fp) 是"写入文件对象 fp"，会调用 fp.write() 导致 'dict' object has no attribute 'write'
    return json.dumps({
        "state":"success",
        "id":"evn"+runtime.tool_call_id,
        "content":result["messages"][-1].text
    })

#实现返回“结构化”的结果
@tool
def send_email(request:str,runtime:ToolRuntime)->str:
    '''
    专门负责发送邮件相关的工具
    当任务涉及发送邮件时，可以调用此工具完成需求
    '''
    result=ExampleEmailAgent.email_agent.invoke(
        {"messages":[{"role":"user","content":request}]}
    )
    return result["messages"][-1].text

SUPERVISOR_PROMPT = (
"你是⼀个有⽤的个⼈助理。"
"你可以安排⽇历事件和发送电⼦邮件。"
"将⽤⼾请求分解为适当的⼯具调⽤并协调结果。"
"当请求涉及多个操作时，按顺序使⽤多个⼯具。"
)


#定义agent
model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

#创建线程
config={"configurable":{"thread_id":"111"}}

main_agent=create_agent(
    model=model,
    system_prompt=SUPERVISOR_PROMPT,
    tools=[shcedule_calendar, send_email],
    checkpointer=InMemorySaver(),
)

#测试agent（采取“流式输出”更好观察结果）
#中断测试
# result=main_agent.invoke(
#     {"messages":[{"role":"user","content":"我将要安排2026-9-7日下午2点安排技术会议"
#                                           ",我想要通知技术一组的成员，让他们关注模型涉及的相关信息,相关的邮箱地址:[""111.com,222.com"}]},
#     config=config,
#     version="v2"
# )
# print(result.interrupts.value)

#中断

#查看interrupts结构
# for chunk in main_agent.stream({"messages":[{"role":"user","content":"我将要安排2026-9-7日下午2点安排技术会议,我想要通知技术一组的成员，让他们关注模型涉及的相关信息,相关的邮箱地址:["
#                                           "111@qq.com,222@qq.com]"}]}, config=config, version="v2"):
#       data = chunk.get("data", {})
#       if "__interrupt__" in data:                      # 中断信息在这里
#           for interrupt in data["__interrupt__"]:
#               print(interrupt)
#               for request in interrupt.value["action_requests"]:
#                   print(f"等待审批 工具: {request['name']}")
#                   print(f"参数: {request['args']}")
#                   print(f"说明: {request['description']}")
#       else:
#           for node_update in data.values():            # model/tools 节点更新
#               if isinstance(node_update, dict):
#                   for message in node_update.get("messages", []):
#                       message.pretty_print()
#结果
#Interrupt(
# value={'action_requests': [{'name': 'send_email',
#        'args': {'to': ['111@qq.com', '222@qq.com'],
#                 'subject': '技术会议通知（2026-9-7 下午2点）',
#                 'body': '各位技术一组成员：\n\n现通知，2026年9月7日（星期一）下午2点将召开技术会议，请提前安排好时间准时参加。\n\n会议涉及模型相关内容，请各位关注模型涉及的相关信息，并提前做好准备。\n\n特此通知。\n\n技术一组长'},
#        'description': "等待发送email的审批……\n\nTool: send_email\n
#        Args: {'to': ['111@qq.com', '222@qq.com'],
#               'subject': '技术会议通知（2026-9-7 下午2点）',
#               'body': '各位技术一组成员：\\n\\n现通知，2026年9月7日（星期一）下午2点将召开技术会议，请提前安排好时间准时参加。\\n\\n会议涉及模型相关内容，请各位关注模型涉及的相关信息，并提前做好准备。\\n\\n特此通知。\\n\\n技术一组长'}"}],
#        'review_configs': [{'action_name': 'send_email', 'allowed_decisions': ['approve', 'edit', 'reject', 'respond']}]
#       },
# id='f0b05c289716e146575cb67b8920bfa0')
#stream产出的chunk结构:
#{'type': 'updates', 'ns': (), 'data': {'model': {'messages': [AIMessage...]}}}
#{'type': 'updates', 'ns': (), 'data': {'__interrupt__': (Interrupt(value={...}),)}}
#中断
intercepts=[]
for chunk in main_agent.stream(
    {"messages":[{"role":"user","content":"我将要安排2026-9-7日下午2点安排技术会议,我想要通知技术一组的成员，让他们关注模型涉及的相关信息,相关的邮箱地址:["
                                          "111@qq.com,222@qq.com]"}]},
    config=config,
    version="v2"
):
    data=chunk.get("data",{})
    if "__interrupt__" in data:
        for interrupt in data["__interrupt__"]:
            intercepts.append(interrupt)
            for request in interrupt.value["action_requests"]:
                print(f"\n中断 id: {interrupt.id}")
                print(f"等待审批 工具: {request['name']}")
                print(f"参数: {request['args']}")
                print(f"说明: {request['description']}")

    for update in chunk.values():
        if isinstance(update, dict):
            for message in update.get("messages", []):
                message.pretty_print()

#恢复
resume = {}
for interrupt_ in intercepts:
    if interrupt_.value["review_configs"][0]["action_name"] == "send_email":
        # 编辑邮件操作
        edited_action = interrupt_.value["action_requests"][0].copy()
        edited_action["args"]["subject"] = "模型制作提醒"
        resume[interrupt_.id] = {
            "decisions": [{"type": "edit", "edited_action": edited_action}]
        }
    else:
        # 批准其他操作
        resume[interrupt_.id] = {"decisions": [{"type": "approve"}]}

#日程安排审批恢复+发送email的审批
interrupts = []
for step in main_agent.stream(
Command(resume=resume),
config,
):
    for update in step.values():
        if isinstance(update, dict):
            for message in update.get("messages", []):
                message.pretty_print()
        else:
            interrupt_ = update[0]
            interrupts.append(interrupt_)
            print(f"\n中断: {interrupt_.id}")


#恢复
resume = {}
for interrupt_ in intercepts:
    if interrupt_.value["review_configs"][0]["action_name"] == "send_email":
        # 编辑邮件操作
        edited_action = interrupt_.value["action_requests"][0].copy()
        edited_action["args"]["subject"] = "模型制作提醒"
        resume[interrupt_.id] = {
            "decisions": [{"type": "edit", "edited_action": edited_action}]
        }
    else:
        # 批准其他操作
        resume[interrupt_.id] = {"decisions": [{"type": "approve"}]}

#发送email的恢复
interrupts = []
for step in main_agent.stream(
Command(resume=resume),
config,
):
    for update in step.values():
        if isinstance(update, dict):
            for message in update.get("messages", []):
                message.pretty_print()
        else:
            interrupt_ = update[0]
            interrupts.append(interrupt_)
            print(f"\n中断: {interrupt_.id}")

