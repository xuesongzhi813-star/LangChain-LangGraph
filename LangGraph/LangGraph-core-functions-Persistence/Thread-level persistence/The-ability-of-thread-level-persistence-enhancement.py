import operator
from typing import TypedDict, Annotated

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

#准备工作:
#定义聊天模型
model=init_chat_model(
    model="deepseek-v4-flash"
)
#定义搜索工具
#定义工具
search_tool=TavilySearch(max_results=3)
tools=[search_tool]
with_tool_model=model.bind_tools(tools)

#1.定义状态
class MessageState(TypedDict):
    #定义一个“消息列表”作为状态存储（这样在图的执行过程中，总是不断更新的）-->存储所有的“历史消息”
    messages:Annotated[list[AnyMessage],operator.add]

    #定义LLM的调用次数
    llm_calls:int

#2.定义节点
#定义LLM调用节点
def llm_call_node(state:MessageState):
    '''
    LLM调用节点的两种可能：
    1.LLM判断无需调用工具，返回的AIMessage中无tool_call直接返回结果结束
    2.LLM判断需要调用工具，返回的AIMessage中有tool_call跳转“工具节点”调用工具
    '''
    #从“历史消息”列表中拿到最新的消息-->HumanMessage
    #拼凑成系统提示词，传给LLM
    #状态更新
    return {
        "messages":[
            with_tool_model.invoke(
                [
                    SystemMessage(
                        content="你是一个乐于助人的助手，支持调用工具进行搜索"
                    )
                ]
                +state["messages"]
            )
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }


tools_by_name = {tool.name: tool for tool in tools} #
#定义工具调用节点
def tool_call_node(state:MessageState):
    '''
    从“历史消息状态列表”中获取到最新的消息-->AIMessage从而得到tool_call
     -->从tool_call中得到调用哪个工具
    '''
    #从“历史消息状态列表”中获取AIMessage
    latest_message=state["messages"][-1]
    result=[]
    #遍历所有到所有的tool_call（要求调用的工具），并且比对是否有这个工具
    for tool_call in latest_message.tool_calls:
        tool=tools_by_name[tool_call["name"]] #根据名字获取到工具
        fianl=tool.invoke(tool_call["args"]) #调用工具
        result.append(ToolMessage(content=str(fianl),
                                  tool_call_id=tool_call["id"])) #消息列表添加

    #更新状态
    return {
        "messages":result,
    }

#3.定义图
search_agent_system=StateGraph(MessageState)

#4.添加节点
search_agent_system.add_node(llm_call_node)
search_agent_system.add_node(tool_call_node)

#5.添加边
search_agent_system.add_edge(START,"llm_call_node") #固定边

#定义“决策函数”（路由）
def decide_way(
        state:MessageState,
):
    '''
    根据最新消息AIMessage中是否有tool_call来判断走向：
    有tool_call:走工具节点
    无tool_call:直接返回结果，走END
    '''
    #先获取到最新的消息
    latest_message=state["messages"][-1]
    if latest_message.tool_calls:
        return "tool_call_node"
    else:
        return END
#条件边
search_agent_system.add_conditional_edges("llm_call_node",decide_way,["tool_call_node",END])
#工具节点执行完回到LLM节点，形成循环
search_agent_system.add_edge("tool_call_node","llm_call_node")

#6.编译图

DB_URI = "postgresql://postgres:2096867998@81.71.3.45:5432/postgres"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    search_agent_system = search_agent_system.compile(checkpointer=checkpointer)

    # 创建“单次会话线程”
    config = {"configurable": {"thread_id": "111"}}

    # 注！！！：内存级存储，只能在同一次执行中进行多次对话，不像数据库重启一次都可以进行
    # 第一次对话
    # search_agent_system.invoke(
    #     {"messages": [{"role": "user", "content": "今天南京的天气如何"}]},
    #     config=config
    # )["messages"][-1].pretty_print()
    #
    # # 第二次对话
    # result = search_agent_system.invoke(
    #     {"messages": [{"role": "user", "content": "刚才我们聊了什么"}]},
    #     config=config
    # )
    # result["messages"][-1].pretty_print()

# 额外能力1：获取最新“状态快照”-->依靠编译好的“图对象”（因为存储在存储库中，因此可以读取出来）
    #StateSnapshot(
    # values={'messages': [], 'llm_calls': 6},
    # next=(),
    # config={'configurable': {'thread_id': '111', 'checkpoint_ns': '', 'checkpoint_id': '1f1b59d5-d112-6a1a-800e-bf6b7253b351'}},
    # metadata={'step': 14, 'source': 'loop', 'parents': {}},
    # created_at='2026-09-21T09:18:10.109487+00:00',
    # parent_config={'configurable': {'thread_id': '111', 'checkpoint_ns': '', 'checkpoint_id': '1f1b59d5-b988-69b6-800d-d034e6606079'}},
    # tasks=(),
    # interrupts=())

    # print(search_agent_system.get_state(config))
    #
    # #额外能力2：获取历史所有的“状态快照”-->依靠“编译好的图对象”
    # history_list=list(search_agent_system.get_state_history(config))
    # print(history_list)

    #额外能力3：重放功能-->从某个“状态快照”开始重新执行一遍（走一遍流程，不会再次添加，相当于是读档）



