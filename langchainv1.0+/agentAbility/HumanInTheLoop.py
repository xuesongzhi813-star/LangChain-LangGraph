import os

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

model=ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    #关闭思考模式，否则deepseek可能无法稳定发起工具调用，导致没有中断产生
    extra_body={"thinking": {"type": "disabled"}},
)

@tool
def remove_file(path: str) -> str:
    """Delete a file from the filesystem."""
    return f"Deleted {path}"


@tool
def fetch_file(path: str) -> str:
    """Read a file from the filesystem."""
    return f"Contents of {path}"


@tool
def notify_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Sent email to {to}"



agent=create_agent(
    model=model,
    tools=[remove_file, fetch_file, notify_email],
    #系统提示词授权直接执行，否则模型可能出于安全考虑反问/拒绝，导致不会产生中断
    system_prompt="你是一个文件管理助手，用户已授权你执行删除等操作，收到指令后立即执行，无需二次确认或反问",
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={
            "remove_file":True,
            "fetch_file":False,
            "notify_email":{"allowed_decisions":["approve","edit"]}
        },
        description_prefix="人工介入，管理工具执行情况",
    ),],
    checkpointer=InMemorySaver(),
)

#应对中断
#因为，调用中断--->处理--->再恢复工具调用；涉及线程安全，需要指定在“同一个线程下进行”
#验证删除文件-->approve & reject策略
config={"configurable":{"thread_id":"1"}}
result=agent.invoke(
    #注意：提示词要明确指令“直接删除、不要先读文件、不要反问”，
    #否则模型可能先调用fetch_file（未被监控）或反问用户，导致不会产生中断
    {"messages":[{"role":"user","content":"请直接删除文件 C:/aaa，立即执行，不要先读文件，也不要反问确认"}]},
    config=config,
    #注意：必须指定version="v2"，invoke才返回带 .interrupts 属性的 GraphOutput 对象；
    #不指定时返回普通dict，访问 .interrupts 会报 AttributeError: 'dict' object has no attribute 'interrupts'
    version="v2",
)

#测试edit策略
# result=agent.invoke(
#     {"messages":[{"role":"user","content":"请发送信息给王鹏,摘要是你好，内容是最近还好吗"}]},
#     config=config,
#     #注意：必须指定version="v2"，invoke才返回带 .interrupts 属性的 GraphOutput 对象；
#     #不指定时返回普通dict，访问 .interrupts 会报 AttributeError: 'dict' object has no attribute 'interrupts'
#     version="v2",
# )

print(result.interrupts)
#注意：interrupts 是一个元组；模型没有调用“被监控的工具”时它就是空的 ()
# if not result.interrupts:
#     print("没有产生中断，模型最后一条消息：")
#     print(result.value["messages"][-1].content)
# else:
#     for interrupt in result.interrupts:
#         #interrupt.value 才是中断的载荷：包含待人工审批的工具调用的详情
#         for request in interrupt.value["action_requests"]:
#             print(f"等待人工审批 工具: {request['name']}")
#             print(f"参数: {request['args']}")
#             print(f"说明: {request['description']}")

#恢复工具调用
result=agent.invoke(
    #人工决策结果
    # Command(
    #     resume={"decisions":[{"type":"approve"}]}
    # ),

    # Command(
    #     resume={"decisions":[
    #         {
    #             "type":"edit",
    #             "edited_action":{
    #                 "name":"notify_email",
    #                 "args":{"to":"张三","subject":"你好","body":"最近还好吗"},
    #             },
    #         },
    #     ]},
    # ),

    Command(
        resume={"decisions":[{"type":"reject",
                              "message":"你暂时没有权限删除这个文件"}]}
    ),
    config=config,
    version="v2",
)
#注意：恢复执行完成后 interrupts 为空元组是正常的——中断只在“发生时”的那次调用结果里
print("恢复执行后的最终回复：", result.value["messages"][-1].content)

