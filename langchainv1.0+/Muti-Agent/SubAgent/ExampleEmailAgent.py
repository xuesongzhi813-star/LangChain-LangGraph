import os

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def send_email(
to: list[str], # email 地址列表
subject: str,
body: str
) -> str:
    """通过电⼦邮件 API 发送电⼦邮件。需要提供格式正确的收件⼈地址。"""
    # 说明：实际上，这会调⽤诸如 Gmail API 等服务。
    return f"已向 {', '.join(to)} 发送电⼦邮件 - 主题：{subject}"

EMAIL_AGENT_PROMPT = (
"你是⼀个电⼦邮件助⼿。"
"根据⾃然语⾔请求撰写专业的电⼦邮件。"
"提取收件⼈信息，并拟定合适的主题⾏与正⽂内容。"
"使⽤ send_email 发送邮件。"
"在最终回复中务必确认已发送的内容。"
)


#定义agent
model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

email_agent=create_agent(
    model=model,
    system_prompt="",
    tools=[send_email],
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={"send_email":True},
        description_prefix="等待发送email的审批……"
    )]
)

# #测试agent（采取“流式输出”更好观察结果）
# for chunk in email_agent.stream(
#     {"messages":[{"role":"user","content":"我想要通知技术一组的成员，让他们关注模型涉及的相关信息"}]}
# ):
#     for item in chunk.values():
#         for message in item.get("messages",[]):
#             message.pretty_print()

