from typing import Literal

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agent.Recommend import recommend_graph
from agent.Reserve import reserve_graph
from agent.Extend import extend_graph
from agent.common.Context import ContextSchema
from agent.node.Main import get_user_info, identify_question, need_reserve, return_info
from agent.state.main import MainState, NeedReserveState

builder=StateGraph(MainState,context_schema=ContextSchema)

#添加节点
builder.add_node(get_user_info)
builder.add_node(identify_question)
builder.add_node(need_reserve)
builder.add_node("get_info",return_info)

#开始添加“子图”节点
builder.add_node("recommend_house",recommend_graph)
builder.add_node("reserve_house",reserve_graph)
builder.add_node("others",extend_graph)

#添加边
builder.add_edge(START,"get_user_info")
builder.add_edge("get_user_info","identify_question")
#路由条件边
def router_way(state:MainState)->Literal["recommend_house","reserve_house","get_info","others"]:
    '''根据状态中“user_intent”路由决定下一个节点'''
    order=state["user_intent"]
    if order=="recommend_house":
        return "recommend_house"
    elif order=="reserve_house":
        return "reserve_house"
    elif order=="get_info":
        return "get_info"
    else:
        return "others"

builder.add_conditional_edges("identify_question",router_way,{"recommend_house","reserve_house","get_info","others"})

#推荐子图
builder.add_edge("recommend_house","need_reserve")
def select_next(state:NeedReserveState):
    '''根据“私有状态”，判定下一个节点走向'''
    answer=state["needReserve"]
    if answer=="需要":
        return "reserve_house"
    else:
        return "__end__"

builder.add_conditional_edges("need_reserve",select_next,{"reserve_house":"reserve_house","__end__":END})

#预定子图
builder.add_edge("reserve_house",END)

#其他问题应答子图
builder.add_edge("others",END)

#返回个人信息
builder.add_edge("get_info",END)

graph=builder.compile()

