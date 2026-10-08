from langchain_core.messages import SystemMessage, filter_messages, HumanMessage
from langgraph.runtime import Runtime
from langgraph.store.base import BaseStore
from langgraph.types import interrupt
from pydantic import BaseModel, Field
from typing_extensions import Literal

from agent.common.Context import ContextSchema
from agent.common.LLM import model
from agent.state.main import MainState, NeedReserveState


#定义节点:获取用户偏好信息
def get_user_info(state:MainState,runtime:Runtime[ContextSchema],*,store:BaseStore):
    '''通过上下文，获取到用户偏好信息'''
    user_id=runtime.context.user_id
    namespace=(user_id,"preference")
    pref_result=store.search(namespace) #获取到结果
    if pref_result and pref_result[0]:
        pref=pref_result[0].value
        #store中可能存的是UserPreference实例（历史版本写入的），统一转成dict再使用
        if not isinstance(pref,dict):
            pref=pref.model_dump()
        return {
            "user_preference": pref,
        }
    else:
        return {"user_preference": {}}

#定义节点:对用户意图进行分流-->基于LLM的结构化输出实现
class UserOrder(BaseModel):
    user_intent:Literal["recommend_house","reserve_house","get_info","others"]=Field(description="根据⽤⼾问题描述判断问题类型：推荐房源、预定房源、获取信息、其他内容")

def identify_question(state:MainState):
    prompt='''你是一个根据描述提取信息的提取专家。请从用户的描述中提取想要咨询的相关信息。"
                    "严谨根据语义推断信息，但是不能猜测或者编造信息。
    '''
    result=model.with_structured_output(UserOrder,method="function_calling").invoke([SystemMessage(content=prompt)]+[state["messages"][-1]])
    return {"user_intent":result.user_intent}

#定义节点:确认“是否进行预定”
def need_reserve(state:MainState)->NeedReserveState:
    '''返回的是一个私有状态，只在节点传递间存在，最后结果中，不会存在'''
    prompt = f"已经为您推荐合适的房源，是否需要帮您预订房源？\n"
    prompt += "如果不需要,请输入'**不需要**'。\n"
    prompt += "如果需要,请输入'**需要**'。\n(注意输入其它值无效)\n"
    #使用“中断”实现
    answer=interrupt(prompt)
    return {"needReserve":answer}

#定义节点:返回“个人偏好信息”
def return_info(state:MainState):
    #先从状态中获取到（参考答案）
    user_preference=state.get("user_preference",{})
    #“预定过的房源”是列表形式，比较特殊，要特殊处理
    reserved_info=user_preference.get("reserve_list",[])
    if reserved_info:
        # 有预定过的信息
        reserved_str = "\n"
        for i, item in enumerate(reserved_info, 1):
            reserved_str += f"{i}. 预定工单ID: {item.get('order_id')}，" \
                            f"房源标题：{item.get('title')}，" \
                            f"预定电话：{item.get('phone_number')}\n"
    else:
        # 没有预定
        reserved_str = "无"
    #还要获取到，用户本次的问题（需要解决的问题）
    user_message=filter_messages(state["messages"],include_types="human")
    #LLM根据“问题”+“参考答案”-->组织出最终结果
    result=model.invoke([SystemMessage(content="""你是一个乐于助人的助手，可以根据用户偏好信息进行回复。
如果有的偏好数据为空，不要猜测或编造数据。
不要直接回复偏好数据是什么，要结合问题进行生动回复。
如果问题与用户偏好数据无关，直接回复即可。""") ,
                  HumanMessage(content=f"当前用户的偏好数据如下:"
                                       f"1.用户的租房最大预算:{user_preference.get("max_budget")}"
                                       f"2.用户的租房最低预算:{user_preference.get("min_budget")}"
                                       f"3.用户的历史预定房源信息:{reserved_str}")]+[user_message[-1]])
    return {"messages":[result]}
















