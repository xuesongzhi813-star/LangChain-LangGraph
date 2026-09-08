import os
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolRuntime
from langgraph.store.memory import InMemoryStore

#定义系统提示词
SYSTEM_PROMPT=("你是一个乐于助人的帮手，现在对你提供了两个工具:"
               "你可以通过search_for_weather方法查询当地的天气状况"
               "你可以通过search_for_id查询到用户的id信息"
               "注意！必须在有城市状况的情况下才能调用查询天气方法"
               "当没有城市的情况下，你可以调用查询用户id的方法，查询到用户当前所处在的城市")

#定义上下文
@dataclass
class Context:
    '''这个上下文中，只存储用户的id'''
    user_id : str

#定义输出格式
@dataclass
class StructuredResponse:
    '''agent的响应格式'''
    #诙谐的回答
    funny_response: str
    #天气的详细信息
    weather_message: str


#定义工具
@tool
def search_for_weather(city:str)->str:
    '''通过这个工具查询天气'''
    return f"{city}总是阳光明媚"

@tool
def search_for_id(runtime:ToolRuntime[Context])->str:
    """通过这个工具从store中查询用户id"""
    #通过用户id将用户信息存储到store（长期存储），用户查询通过id去store寻找
    #获取store，userId（运行时上下文中）
    user_id=runtime.context.user_id
    memory_store=runtime.store

    #工具中使用store：put(命名空间元组, key, value字典)，get(命名空间元组, key)
    memory_store.put(("users",),user_id,{"name":f"name_{user_id}"})
    user_info=memory_store.get(("users",),user_id)
    print(f"user_name:{user_info.value.get('name')}")
    return "北京" if user_id=="1" else "上海"


#定义一个模型
#注意：deepseek-v4默认开启思考模式，思考模式不支持tool_choice，
#而response_format(默认ToolStrategy)需要强制tool_choice，所以必须关闭思考
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    extra_body={"thinking": {"type": "disabled"}},#关闭思考模式，否则无法调用工具
)

#定义一个agent
agent=create_agent(
    model=model,
    name="weather_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[search_for_weather,search_for_id],
    checkpointer=InMemorySaver(),
    context_schema=Context,
    store=InMemoryStore(),
    response_format=StructuredResponse,
)

#获取一个当前线程（起到上下文作用）
config={"configurable":{"thread_id":"1"}}
#测试Agent根据上下文自主决策
# response=agent.invoke(
#     {"messages":[{"role":"user","content":"我在的地方，天气怎么样？"}]},
#     config=config,
#     context=Context(user_id="1"),
# )
# print(response)

#测试agent多轮对话+输出格式
response=agent.invoke(
    {"messages":[{"role":"user","content":"我在的地方，天气怎么样？"}]},
    config=config,
    context=Context(user_id="2"),
)
print(response["structured_response"])

#测试
response2=agent.invoke(
{"messages":[{"role":"user","content":"谢谢"}]},
    config=config,
    context=Context(user_id="2"),
)
print(response2["structured_response"])