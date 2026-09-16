import os
from typing import TypedDict, List, Callable

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse, ExtendedModelResponse
from langchain.agents.middleware.types import ResponseT
from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from langgraph.typing import ContextT


#定义Skill专项能力的组成
class Skill(TypedDict):
    name: str
    description: str
    content: str

# 定义完整的 Skills 列表
SKILLS: list[Skill] = [
{
"name": "sales_analytics",
"description": "⽤于销售数据分析的数据库模式与业务逻辑，包含客⼾、订单和收⼊。",
"content": """# 销售分析模式
## 数据表
### customers (客⼾表)
- customer_id (主键), name, email, signup_date
- status (active/inactive), customer_tier (bronze/silver/gold/platinum)
### orders (订单表)
- order_id (主键), customer_id (外键), order_date
- status (pending/completed/cancelled/refunded), total_amount
### order_items (订单项表)
- item_id (主键), order_id (外键), product_id, quantity, unit_price
## 业务逻辑
**⾼价值订单**: total_amount > 1000
**收⼊计算**: 仅统计 status = 'completed' 的订单。
"""
},
{
"name": "inventory_management",
"description": "⽤于库存跟踪的数据库模式与业务逻辑，包含产品、仓库和库存⽔平。",
"content": """# 库存管理模式
## 数据表
### products (产品表)
- product_id (主键), product_name, sku, category, unit_cost, reorder_point
### warehouses (仓库表)
- warehouse_id (主键), warehouse_name, location, capacity
### inventory (库存表)
- inventory_id (主键), product_id (外键), warehouse_id (外键), quantity_on_hand
## 业务逻辑
**可⽤库存**: quantity_on_hand > 0
**需补货产品**: 各仓库 quantity_on_hand 总和 <= reorder_point
"""
},
]



#自定义工具，真正导入skill的正文
@tool
def put_skill(
        skill_name:str
)->str:
    """将 Skills 的完整内容加载到智能体的上下⽂中。
    当你需要处理特定类型请求的详细信息时使⽤此⼯具。
    它将为你提供该 Skills 领域的全⾯指令、策略和指南。
    Args:
    skill_name: 要加载的 Skills 名称 (例如 "sales_analytics")
    """
    for skill in SKILLS:
        if skill["name"] == skill_name:
            return f"已经返回对应的skill,name:{skill_name},description:{skill['description']},content:{skill['content']}"

    #没有找到对应的skill
    available_list=",".join(s["name"] for s in SKILLS)
    return f"当前Agent不支持{skill_name}的skill，你可以在这部分支持的skill中选择{available_list}"


class selfDefineMiddleware(AgentMiddleware):

    #供给agent调用的工具
    tools = [put_skill]

    #自定义初始化方法，将有哪些skill录入
    def __init__(self):
        '''把提供给Agent调用的Skill基本信息存储'''
        skill_list=[]
        for skill in SKILLS:
            skill_list.append(f"\n\nskill的名称:{skill["name"]},skill的基本描述:{skill["description"]}\n\n")
        self.skill_prompt=skill_list

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        '''替代“系统提示词”从而让Agent调用工具去获取对应的Skill正文'''
        '''先导入可以选用的Skill附录给Agent'''

        skill_Literal=(f"##目前支持的Skill附录\n\n##{self.skill_prompt}\n\n,"
                       f"当你需要根据问题寻找对应专项能力的Skill，可以从此目录中去查找")

        #构造新的“系统提示词”
        new_content=request.system_message.content_blocks+[{"type":"text","text":skill_Literal}]
        System_Message=SystemMessage(content=new_content)
        request.override(system_message=System_Message)
        return handler(request)



model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
agent=create_agent(
    model=model,
    tools=[put_skill],
    system_prompt="你是⼀个SQL查询助⼿，帮助⽤⼾编写针对业务数据库的查询。",
    middleware=[selfDefineMiddleware()],
    checkpointer=InMemorySaver()
)

config={"configurable":{"thread_id":"111"}}
result=agent.invoke(
    {"messages":[{"role":"user","content":"帮我生成，插入学生信息的SQL语句"}]},
    config=config,
)
print(result)
