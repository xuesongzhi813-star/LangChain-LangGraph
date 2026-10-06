import uuid
from typing import Annotated, Any

from agent.common.Context import ContextSchema
from agent.common.LLM import model
from agent.common.store import UserPreference, ReserveList
from agent.state.reserve import ReserveState
from click import prompt
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime, InjectedStore, ToolNode
from langgraph.types import interrupt


#定义节点:获取房源名称
def get_house_name(state:ReserveState):
    '''循环中断-->直至获取不为空'''
    prompt="请输入你要预定的房源名称"
    while True:
        response=interrupt(prompt)
        #如果不为空，则直接更新
        if response:
            return {"house_name":response}
        else:
            prompt=f"请输入正确的房源名称,{response}不是一个合法的房源名称"

#定义节点:获取预定电话
def get_phone_number(state:ReserveState):
    '''循环中断-->直至获取不为空'''
    prompt="请输入你的预定电话号码"
    while True:
        response=interrupt(prompt)
        #如果不为空，则直接更新
        if response:
            return {"phone_number":response}
        else:
            prompt=f"请输入正确的预定电话,{response}不是一个合法的预定电话"

#定义节点:获取预定身份证信息
def get_id_card(state:ReserveState):
    '''循环中断-->直至获取不为空'''
    prompt="请输入你的预定身份作证信息"
    while True:
        response=interrupt(prompt)
        #如果不为空，则直接更新
        if response:
            return {"id_card":response}
        else:
            prompt=f"请输入正确的预定身份证,{response}不是一个合法的身份证信息"

#定义节点:构建HumanMessage
def add_HumanMessage(state:ReserveState):
    '''整合上述的信息，构建一条HumanMessage追加到历史消息队列，提供给后面的LLM使用'''
    reserve_prompt = """
    根据提供的信息，帮我预定房源。
    - 预定的房源标题：{title}
    - 用户预定号码：{phone_number}
    - 用户身份证号码：{id_card}
        """.format(title=state["house_name"],phone_number=state["phone_number"],id_card=state["id_card"])

    user_message=HumanMessage(content=reserve_prompt)
    return {"messages":[user_message]}

#定义工具节点:生成工单号
#注意，这里在工具中引入“store”持久化，非常重要的书写形式！！！
@tool
def produce_id(house_name:str,phone_number:str,id_card:str,
               runtime:ToolRuntime[ContextSchema],store:Annotated[Any,InjectedStore()])->str:
    '''

    '''
    #1.模拟生成工单号
    order_id=str(uuid.uuid4())

    #2.构建预定信息
    reserve_info=ReserveList(
        order_id=order_id,
        house_name=house_name,
        order_phone=phone_number,
    )

    #3.store持久化存储预定信息
    #先查询，根据结果决策接下来操作
    user_id=runtime.context.user_id
    namespace=(user_id,"preference")
    store_result=store.search(namespace)
    if len(store_result)==0:
        #采取“新增”操作
        store.put(
            namespace,
            str(uuid.uuid4()),
            reserve_info.model_dump(exclude_none=True),
        )
    else:
        #采取“更新”操作：store中可能是UserPreference实例（Recommand_Node写入的），统一转dict再操作
        pres=store_result[0].value
        if not isinstance(pres,dict):
            pres=pres.model_dump()
        pres.setdefault('reserved_info', []).append(reserve_info)
        store.put(
            namespace,
            store_result[0].key,
            pres
        )
    return f"已成功预定房源：{house_name}, 预定工单号为：{order_id}"

produce_tool_node=ToolNode([produce_id])


#定义节点:生成工单信息
def generate_id(state:ReserveState):
    '''本质只是LLM调用工具来生成“工单号”，因此，这里只是生成AIMessage'''

    llm_with_tool=model.bind_tools([produce_id])
    #注意：拼接消息要用列表对列表，取最后一条用切片[-1:]；[SystemMessage]不要再多套一层括号
    system_message=SystemMessage(content="你是一个工单生成的助手，支持调用工具进行房源预定工单生成。支持查看结果并返回最终答案")
    response=llm_with_tool.invoke([system_message]+state["messages"][-2:])
    return {"messages":[response]}







