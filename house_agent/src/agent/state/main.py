from typing import TypedDict

from langgraph.graph import MessagesState


class MainState(MessagesState):
    user_preference:dict #跨会话存储的store中的信息
    user_intent:str #用户本次对话的意图
    

#私有状态，只在“是否预定”节点-->预定子图节点，使用
class NeedReserveState(TypedDict):
    needReserve: str