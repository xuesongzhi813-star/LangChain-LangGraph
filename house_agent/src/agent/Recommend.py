from agent.common.Context import ContextSchema
from agent.node.Recommand_Node import (
    collect_user_info,
    list_tables,
    call_get_schema,
    generate_query,
    check_query,
    get_schema_node,
    run_query_node,
)
from agent.state.recommand import RecommandState
from langgraph.constants import START
from langgraph.graph import END, StateGraph

#构造图
builder=StateGraph(RecommandState,context_schema=ContextSchema)

#添加点
builder.add_node(collect_user_info)
builder.add_node(list_tables)
builder.add_node(call_get_schema)
builder.add_node(generate_query)
builder.add_node(check_query)
builder.add_node("get_schema",get_schema_node)
builder.add_node("run_query",run_query_node)

#添加边
builder.add_edge(START,"collect_user_info")
builder.add_edge("collect_user_info","list_tables")
builder.add_edge("list_tables","call_get_schema")
builder.add_edge("call_get_schema","get_schema")
builder.add_edge("get_schema","generate_query")

#唯一条件边
#生成了SQL-->check；直接生成答案-->END
def should_over(state:RecommandState):
    '''判断是否有tool_call决定走向'''
    last_message=state["messages"][-1]
    #注意：LangChain v1 的 AIMessage 不再支持下标访问，要用属性访问
    if last_message.tool_calls:
        return "check_query"
    else:
        return END

builder.add_conditional_edges("generate_query",should_over,["check_query",END])
builder.add_edge("check_query","run_query")
builder.add_edge("run_query","generate_query")

recommend_graph=builder.compile()






