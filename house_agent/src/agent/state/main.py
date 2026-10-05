from langgraph.graph import MessagesState


class MainState(MessagesState):
    user_preference:dict #跨会话存储的store中的信息