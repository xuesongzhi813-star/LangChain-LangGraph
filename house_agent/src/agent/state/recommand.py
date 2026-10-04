from langgraph.graph import MessagesState


#继承MessagesState，因为节点中，条件判断/正常传递参数，都会涉及Message
#关于子图中涉及的messages:
#输入（HumanMessage），输出（AIMessage）
#获取数据库中的表（必须调用工具，使用手动调用，在一个节点中）:LLM（判定了工具）的AIMessgae(tool_call)-->工具返回ToolMessage-->LLM总结AIMessage(可用哪些表)
#决定是否获取可用表的信息(先要从“历史消息列表”取出上一个的AIMessage)-->AIMessage(tool_call)条件边判断是否调用
#若调用，工具返回ToolMessage(表的详细信息，字段，类型...)
#生成SQL（需要先获取到“可用表的AIMessage”+“表的详细ToolMessage”+“用户指定消息（收集提取的Message）”）-->AIMessage(SQL)
#生成好的SQL-->（执行一遍，当作检验）检验SQL（绑定执行SQL工具的LLM）-->AIMessage(tool_call)-->执行SQL的工具-->ToolMessage（执行结果）
#整合结果（与生成SQL为同一节点）-->AIMessage(也就是输出)
#
#

#同时实现一些，用户推荐条件（用户要求的信息）-->本图中独有的状态
class RecommandState(MessagesState):
    '''用户偏好（主，子图共享状态），适用于用户没有提供必须信息时，可以从中智能化推断，给出更优结果'''
    user_preference:dict

    # 以下是推荐的关键参数
    city: str  # 城市
    budget_min: float  # 最低预算
    budget_max: float  # 最⾼预算
    district: str  # 区域
    room_type: str  # 房屋类型
    orientation: str  # 朝向
    room_count: int  # 推荐数量
    others: str  # 其它要求
