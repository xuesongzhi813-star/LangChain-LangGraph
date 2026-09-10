import os
from typing import Callable

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_openai import ChatOpenAI
from langchain.tools import tool


#定义模型
model=ChatOpenAI(model="deepseek-v4-flash",api_key=os.getenv("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com")

#定义工具
@tool
def public_search(query: str) -> str:
  """公开搜索：⽆需认证即可使⽤，返回基础信息。"""
  print(f"[公开搜索结果] 关于 '{query}' 的基础信息：这是公开可获取的内容。")
  return f"[公开搜索结果] 关于 '{query}' 的基础信息：这是公开可获取的内容。"

@tool
def private_search(query: str) -> str:
     """私有搜索：仅已认证⽤⼾可⽤，返回敏感或个性化数据。"""
     print(f"[私有搜索结果] 关于 '{query}' 的私密数据：仅限认证⽤⼾查看。")
     return f"[私有搜索结果] 关于 '{query}' 的私密数据：仅限认证⽤⼾查看。"

@tool
def advanced_search(query: str) -> str:
    """⾼级搜索：提供深度分析。"""
    print(f"[⾼级搜索结果] 关于 '{query}' 的深度分析报告：包含详细统计和趋势。")
    return f"[⾼级搜索结果] 关于 '{query}' 的深度分析报告：包含详细统计和趋势。"

#拓展agent属性
class ExpanseStatus(AgentState):
    auth:bool

#定义，筛选工具的中间件
@wrap_model_call(state_schema=ExpanseStatus)
def change_tools(
        request:ModelRequest,
        handler:Callable[[ModelRequest],ModelResponse],
)->ModelResponse:
    #根据授权情况决定，调用方法
    autho=request.state.get('auth')
    if not autho:
        tools=[t for t in request.tools if t.name.startswith("public_")]
        #更换
        request=request.override(tools=tools)
    else:
        tools=[t for t in request.tools if t.name.startswith("private_")]
        request=request.override(tools=tools)
    return handler(request)




agent=create_agent(
    model=model,
    tools=[public_search, private_search, advanced_search],
    middleware=[change_tools],
)

# config={"configurable":{"thread_id":"1"}}
print(agent.invoke(
    {"messages": [{"role": "user", "content": "我想知道北京的信息"}],
     "auth":True},

))


