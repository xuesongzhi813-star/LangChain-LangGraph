from langgraph.graph import MessagesState


class ReserveState(MessagesState):
    '''房源预定子图特有的状态'''
    house_name:str
    phone_number:str
    id_card:str

    user_preference:dict

