'''人工决定是否调用工具-->Agent绑定“人工交互”中间件的底层'''
import operator
import os
from typing import TypedDict, Annotated

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


#定义工具
@tool
def send_email(
        subject:str,
        to:str,
        content:str,
):
    '''发送email的工具'''
    response=interrupt(
        {
            "question":"是否批准本封邮件的发送",
            "subject":subject,
            "to":to,
            "content":content,
         }
    )
    if response["decision"]=="同意":
        #更新一遍参数，可能修改了
        final_subject=response.get("subject",subject)
        final_to=response.get("to",to)
        final_content=response.get("content",content)
        email_info=f"收件人:{final_to},邮件主题:{final_subject},邮件内容:{final_content}"
        print(f"【发送成功】:{email_info}")
        return email_info
    return "已拦截邮件的发送"

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
with_tool_model=model.bind_tools([send_email])

#定义状态
class State(TypedDict):
    messages:Annotated[list[str],operator.add]


#定义节点
def llm_call_node(state:State):
    '''调用llm，判断问题是否需要调用工具'''
    response=with_tool_model.invoke([SystemMessage(content="你⽀持调⽤⼯具进⾏邮件发送。")]
        +state["messages"])
    #判断是否有llm_call
    if response.tool_calls:
        #如果有tool_call则执行调用工具
        tool_call=response.tool_calls[0]
        result=send_email.invoke(tool_call["args"])
        return {
            "messages":[ToolMessage(content=result,tool_call_id=tool_call["id"])],
        }

    return {
        "messages":[response]
    }


#定义图，添加点，添加边
builder=StateGraph(State)

builder.add_node(llm_call_node)

builder.add_edge(START,"llm_call_node")
builder.add_edge("llm_call_node",END)

graph=builder.compile(checkpointer=InMemorySaver())

config={"configurable":{"thread_id":"1"}}
result1=graph.invoke({"messages":[HumanMessage(content="帮我发一封邮件到Bob@qq.com，主题是请假信，因为需要回老家")]},config=config)
print(result1)

result2=graph.invoke(Command(resume={"decision":"同意","subject":"病假信","content":"看牙医"}),config=config)
print(result2)
for msg in result2["messages"]:
    msg.pretty_print()





