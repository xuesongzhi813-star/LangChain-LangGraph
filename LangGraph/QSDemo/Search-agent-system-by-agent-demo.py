import operator
import os
from typing import Annotated, Any, Callable, TypedDict

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse, ExtendedModelResponse
from langchain.agents.middleware.types import StateT, ResponseT
from langchain_core.messages import AnyMessage, ToolMessage, AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command
from langgraph.typing import ContextT

#定义搜索工具
search_tool=TavilySearch(max_results=3)

#1.定义agent状态
class MessageState(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]  #消息历史使用add_messages拼接更新（按id去重追加，比operator.add更安全）
    llm_calls:int

#2.定义中间件-->更新状态
class SelfMiddleware(AgentMiddleware):
    def after_model(self, state: MessageState, runtime: Runtime) -> dict[str, Any] | None:
        '''在LLM调用之后，更新llm_calls的中间件'''
        return {
            "llm_calls":state.get("llm_calls",0)+1
        }

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse | AIMessage | ExtendedModelResponse:
        '''构建系统提示词'''
        base_prompt="你是一名乐于助人的助手，可以借助搜索工具解决一些问题，根据问题类型来决定你是否使用搜索工具"
        request.override(system_message=SystemMessage(content=base_prompt))
        return handler(request)


    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        '''打印工具执行的日志'''
        print(f"准备调用工具{request.tool_call['name']}")
        result=handler(request)
        print(f"调用工具结束")
        return result

#3.定义节点-->本质定义agent，将先前llm调用节点+工具执行节点-->整合“agent‘节点
model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
agent=create_agent(
    model=model,
    tools=[search_tool],
    middleware=[SelfMiddleware()],
    state_schema=MessageState,  #扩展agent内建状态，让llm_calls成为合法的状态字段
)

def agent_node(
  state:MessageState
):
    #create_agent返回的是编译后的图，invoke的输入是状态字典，而不是消息列表
    result=agent.invoke(
        {"messages":state["messages"]}
    )
    #将agent维护的messages全部取出，存入历史消息列表
    #（外层状态用了add_messages，重复的HumanMessage会按id去重，不会重复追加）
    #同时把agent内部统计的llm_calls同步到外层状态
    return {
        "messages":result["messages"],
        "llm_calls":result.get("llm_calls",0)
    }


#4.定义图
search_agent_system=StateGraph(MessageState)

#5.添加节点
search_agent_system.add_node("agent_node",agent_node)

#6.添加边
search_agent_system.add_edge(START,"agent_node")
search_agent_system.add_edge("agent_node",END)

#编译+测试
search_agent_system=search_agent_system.compile()
response=search_agent_system.invoke(
    {"messages":[HumanMessage(content="南京今天的天气如何")]}
)

#关于LLM调用次数是不定的，agent会根据查询的结果，若结果不完整，会重新调用
print(f"LLM的总调用次数为:{response["llm_calls"]}")
for m in response["messages"]:
    m.pretty_print()

