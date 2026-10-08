from langgraph.constants import START, END
from langgraph.graph import StateGraph, MessagesState

from agent.common.Context import ContextSchema
from agent.node.Extend import extend_node

builder=StateGraph(MessagesState,context_schema=ContextSchema)

builder.add_node(extend_node)

builder.add_edge(START,"extend_node")
builder.add_edge("extend_node",END)

extend_graph=builder.compile()


