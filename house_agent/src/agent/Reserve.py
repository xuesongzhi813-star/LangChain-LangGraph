from agent.common.Context import ContextSchema
from agent.node.Reserve_Node import get_house_name, get_phone_number, get_id_card, add_HumanMessage, generate_id, \
    produce_tool_node
from agent.state.reserve import ReserveState
from langgraph.constants import START
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import tools_condition

builder=StateGraph(ReserveState,context_schema=ContextSchema)

#添加点
builder.add_sequence([get_house_name,get_phone_number,get_id_card,add_HumanMessage,generate_id])
builder.add_node("tool_node",produce_tool_node)

#添加边
#入口边：add_sequence只串联节点，不会自动连接START，必须手动添加
builder.add_edge(START,"get_house_name")

#唯一条件边
builder.add_conditional_edges(
    "generate_id",
    tools_condition,
    {
        "tools":"tool_node",
        "__end__":END
    }
                              )
builder.add_edge("tool_node","generate_id",)
reserve_graph=builder.compile()




