import uuid
from typing import Optional, Dict

from langchain_core.messages import filter_messages, HumanMessage, SystemMessage
from langgraph.runtime import Runtime
from langgraph.store.base import BaseStore
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from agent.common.Context import ContextSchema
from agent.common.LLM import model
from agent.common.store import UserPreference
from agent.state.recommand import RecommandState, get_recommend_info


#结构化返回的类
class UserInfo(BaseModel):
    # 定义⽤⼾信息的数据模型(结构化输出)
    city: Optional[str] = Field(
        default=None,
        description="⽤⼾所在或想要租房的城市，例如：西安、北京、上海"
    )
    district: Optional[str] = Field(
        default=None,
        description="⽤⼾想要租房的具体区域或⾏政区，例如：雁塔区、碑林区、海淀区"
    )
    budget_min: Optional[float] = Field(
        default=None,
        description="⽤⼾的最低预算，单位为元/⽉"
    )
    budget_max: Optional[float] = Field(
        default=None,
        description="⽤⼾的最⾼预算，单位为元/⽉"
    )
    room_type: Optional[str] = Field(
        default=None,
        description="房屋类型，例如：整租、合租、公寓、⼀室⼀厅、两室⼀厅"
    )
    orientation: Optional[str] = Field(
        default=None,
        description="房屋朝向，例如：朝南、朝北、东南、南北通透"
    )
    room_count: Optional[int] = Field(
        default=None,
        description="需要推荐的房屋数量"
    )
    others: Optional[str] = Field(
        default=None,
        description="特殊要求，例如：带阳台、独⽴卫⽣间、近地铁、可养宠物、有电梯等"
    )


#定义节点:收集用户信息
def collect_user_info(state:RecommandState,runtime:Runtime[ContextSchema],*,store:BaseStore):
    '''获取用户的信息'''
    #1.用户的最新消息（本次对话信息）+用户偏好数据（可以去主，子图共享状态中取出）
    #用户最新消息获取（过滤历史human消息中最新的一条）
    user_message=filter_messages(
        messages=state["messages"], #过滤对象:历史消息列表
        include_types="human", #保留的消息类型:HumanMessage
    )
    #用户偏好数据
    user_preference_data={}
    user_preference_data=state.get("user_preference")

    #用户偏好中是否有“预期价位”，并且构造成一条消息
    if user_preference_data and (user_preference_data["max_budget"] or user_preference_data["min_budget"]):
        '''偏好中只有“预算”能够帮助筛选'''
        #构造成消息
        user_messages=[
            HumanMessage(content=f"这是该用户的历史偏好:"
                                 f"租房的最低预算:{user_preference_data["min_budget"]}"
                                 f"租房的最高预算:{user_preference_data["max_budget"]}"),
            user_message[-1]
        ]
    else:
        '''没有历史偏好信息补充，直接构造用户最新消息即可'''
        user_messages=[user_message[-1]]

    #2.提取信息->LLM结构化返回“需要的信息”即可-->定义类，作为结构
    llm_with_structed=model.with_structured_output(UserInfo,method="function_calling")
    #协助提取信息的方法，逻辑:系统提示词+用户最新消息-->LLM执行
    def get_message(user_messages)->UserInfo:
        '''提取成输出的结构的方法'''
        #user_messages与提示词一起，构成SystemMessage传给LLM
        system_message = SystemMessage(
            content="""
        你是一个租房需求信息提取专家。请从用户的描述与历史信息中提取租房相关信息。
        如果用户历史偏好信息与最新用户消息冲突，以最新的用户消息为主。
        只提取用户明确提到的信息，不要猜测或推断。
        如果某个信息用户没有提到，就返回null。
        注意预算的单位可能是元/月、元/天等，请统一转换为元/月。
        如果用户提到价格范围，请分别提取最低和最高预算。
        如果用户提到推荐几套房，提取room_count字段。"""
        )
        llm_with_structed.invoke([system_message]+user_messages)

    #这里封装之后，想要再次进行“提取信息”的环节，只需要准备好用户消息列表即可
    #调用“提取信息”的方法
    the_user_info=get_message(user_messages)

    #封装“更新状态”方法-->直接将改变的状态全部构造成dict，节点结束时，直接return即可
    def update_state(current_state:dict,user_info:UserInfo)->dict:
        '''“更新状态”的方法，将UserInfo结构中的，全部转换成字典形式'''
        #current_state就是state中的"推荐关键参数"，此处更新，后续构造SQL参考这些
        if not user_info:
            #如果没有新的用户信息，则照旧
            return current_state
        else:
            user_state=user_info.model_dump(exclude_none=True) #UserInfo转成字典
            current_state.update(user_state)
            return current_state

    #调用“更新状态”的方法:
    update_states={}
    update_states=update_state(update_states,the_user_info)

    #3.中断（用户提供信息缺少“关键信息”），咨询用户传信息->城市+预算范围
    #如何知道缺失信息?-->从update_states（刚提取完）中去看，是否有预算范围+城市
    missing_info=[]
    if not update_states.get("city"):
        missing_info.append("**城市**")
    elif not (update_states.get("budget_min") and update_states.get("budget_max") ):
        missing_info.append("**预算范围**")

    #如果真的有信息缺失，则中断，向用户索求信息
    if missing_info:
        prompt = f"为了给您推荐合适的房源，请提供以下信息:{'，'.join(missing_info)}和其它信息。\n"
        prompt += "如果您不想提供，请输入'**不提供**',我会根据已有信息为您推荐房源。"
        answer=interrupt(prompt) # 中断+接受用户的决策
        #如果用户选择“不提供”，则默认补充
        if str(answer).strip("不提供"):
            if not update_states.get("city"):
                update_states["city"]="随机城市"
            if not update_states.get("budget_min"):
                update_states["budget_min"]="500元/月"
            if not update_states.get("budget_max"):
                update_states["budget_max"]="5000元/月"
            if not update_states.get("room_count"):
                update_states["room_count"]=5
        else:
             #如果用户补充了“必须信息”，则再次进行“提取信息”的函数
             human_message=HumanMessage(content=str(answer))
             get_messages=get_message([human_message])
             #再次更新
             update_states=update_state(update_states,get_messages)

    #4.持久化更新，store中存储的最大预算+最小预算
    #前提：如果更新状态中有“最大预算”/“最小预算”才进行更新
    if update_states.get("budget_min") or update_states.get("budget_max"):
        #获取当前用户的id（上下文）-->确定store中存储的“容器”
        user_id=runtime.context.get("user_id")
        #构造查询的namespace
        namespace=(user_id,"preference")
        #查询store,namespace就像查询的索引，由user_id确认唯一性
        store_result=store.search(namespace)
        #如果result==0，则是新增操作
        if len(store_result)==0:
            '''进行“新增”操作，因为还未有一个用户存在'''
            #构造namespace+key+value存入store
            #先构造value-->跨会话保存的类-->类中有基本要存的数据
            pref=UserPreference(
                max_budget=update_states["budget_max"],
                min_budget=update_states["budget_min"],
            )
            #存入store
            store.put(namespace,uuid.uuid4(),pref)
            #存入共享状态的用户偏好中
            update_states["user_preference"]=pref.model_dump(exclude_none=True)
        else:
            '''进行“更新”操作，要判断存储的预算范围和新的预算范围的包含关系，决定是否更新'''
            pres=store_result[0].value
            new_max_budget=update_states.get("budget_max")
            new_min_budget=update_states.get("budget_min")
            cur_max_budget=pres["max_budget"]
            cur_min_budget=pres["min_budget"]
            update_max_budget=False
            update_min_budget=False
            if new_min_budget is not None and cur_min_budget is not None and (new_min_budget<cur_min_budget):
                '''当“最新的最低预算”存在+小于store中的最低预算则更新'''
                update_min_budget=True
            if new_max_budget is not None and cur_max_budget is not None and (new_max_budget>cur_max_budget):
                '''当“最新的最高预算”存在+大于store中的最高预算则更新'''
                update_max_budget=True

            #如果store中根本不存在，则直接存入（在更新值有效的前提下进行）
            if cur_min_budget is None and new_min_budget is not None:
                update_min_budget=True
            if cur_max_budget is None and new_max_budget is not None:
                update_max_budget=True

            if update_max_budget or update_min_budget:
                if update_max_budget:
                    pres["max_budget"]=new_max_budget
                if update_min_budget:
                    pres["min_budget"]=new_min_budget
                    # 最终更新store
                    store.put(
                        namespace,
                        store_result[0].key,
                        pres
                    )
                    update_states["user_preference"]=pres #此处已经是dict

    #5.最终更新，历史消息列表
    #字典转字符，去添加
    update_states["messages"]=[HumanMessage(content=get_recommend_info(update_states))]
    print(f"已收集用户信息：\n城市：{update_states.get('city')}"
          f"区域：{update_states.get('district')}"
          f"预算：{update_states.get('budget_min')}-{update_states.get('budget_max')}元/月"
          f"房间数：{update_states.get('room_count')}")

    # 返回：覆盖了推荐参数和偏好数据，更新了消息列表
    #因为更新return{}中是字典形式，直接返回字典即可
    return update_states






















