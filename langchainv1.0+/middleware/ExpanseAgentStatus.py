import os
from typing import NotRequired, Any, Callable

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_model, wrap_model_call, ModelRequest, ModelResponse, ExtendedModelResponse
from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime
from langchain.tools import tool
from langgraph.types import Command


#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
extra_body={"thinking": {"type": "disabled"}},#关闭思考模式，否则无法调用工具
)

#定义工具
@tool
def search_for_weather(city:str)->str:
    """这是一个查询天气的工具"""
    return f"{city}总是阳光明媚，晴空万里"


#拓展agent状态：必须通过state_schema传入create_agent，否则更新会被丢弃
class AgentStatus(AgentState):
    """拓展状态：模型调用次数 + 最新一次模型调用消耗的token数"""
    model_call_count: NotRequired[int]
    tool_Tokes_use: NotRequired[int]

#节点定义的，模型中间件：统计模型调用次数
@after_model(state_schema=AgentStatus)
def after_model(state: AgentState,runtime:Runtime)->dict[str, Any] | None:
    return {"model_call_count":state.get("model_call_count",0)+1}

#包装定义的，模型中间件：追踪token消耗
#注意：token信息只在模型响应(ModelResponse)里有，工具响应(ToolMessage)没有result属性
#所以要追踪"调用工具后那次模型调用的token"，必须用wrap_model_call，而不是wrap_tool_call
@wrap_model_call(state_schema=AgentStatus)
def wrap_model_call(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
)->ExtendedModelResponse:
    response = handler(request)#response.result是AIMessage列表
    return ExtendedModelResponse(
            model_response=response,
            command=Command(
                update={"tool_Tokes_use":response.result[-1].response_metadata['token_usage']['total_tokens']}
            )
        )


agent=create_agent(
    model=model,
    tools=[search_for_weather],
    middleware=[after_model,wrap_model_call],
    state_schema=AgentStatus,#传入拓展状态，否则末尾get不到值
)

config={"configurable":{"thread_id":"1"}}
response=agent.invoke(
    {"messages":[{"role":"user","content":"今天贵阳天气如何"}]},
    config=config,
)
print(f"模型调用次数：{response.get("model_call_count")}")
print(f"最新ai消息消耗token数：{response.get("tool_Tokes_use")}")
