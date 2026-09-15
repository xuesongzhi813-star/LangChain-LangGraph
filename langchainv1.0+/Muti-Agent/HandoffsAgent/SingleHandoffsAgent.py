import os
from typing import NotRequired, Literal, Callable

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import SummarizationMiddleware, wrap_model_call, ModelRequest, ModelResponse
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from langgraph.prebuilt import ToolRuntime
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command


#每个状态下，不同的提示词
# 保修收集员提⽰词
WARRANTY_COLLECTOR_PROMPT = """你是⼀名客⼾⽀持专员，负责帮助解决设备问题。
当前步骤：保修验证
在此步骤中，你需要：
1. 询问他们的设备是否在保修期内
2. 根据⽤⼾的回答，使⽤ record_warranty_status 记录他们的回答并进⼊下⼀步
对话要⾃然友好，不要⼀次问多个问题。"""
# 问题分类器提⽰词
ISSUE_CLASSIFIER_PROMPT = """你是⼀名客⼾⽀持专员，负责帮助解决设备问题。
当前步骤：问题分类
客⼾信息：保修状态为 {warranty_status}
在此步骤中，你需要：
1. 请客⼾描述他们遇到的问题
2. 判断问题是硬件问题（物理损坏、部件破损）还是软件问题（应⽤崩溃、性能问题）
3. 使⽤ record_issue_status 记录分类结果并进⼊下⼀步
如果⽆法确定，请在分类前先提出澄清性问题。"""
# 解决⽅案专家提⽰词
RESOLUTION_SPECIALIST_PROMPT = """你是⼀名客⼾⽀持专员，负责帮助解决设备问题。
当前步骤：解决⽅案
客⼾信息：保修状态为 {warranty_status}，问题类型为 {issue_type}
在此步骤中，你需要：
1. 对于软件问题：使⽤ resolve_in_warranty 提供故障排除步骤
2. 对于硬件问题：
- 如果在保修期内：使⽤ resolve_in_warranty 说明保修维修流程
- 如果已过保修期：使⽤ resolve_out_of_warranty 升级以便提供付费维修选项
提供的解决⽅案要具体且有帮助。"""


# 步骤配置：将步骤名称映射到 (提⽰词, ⼯具, 所需状态)
STEP_CONFIG = {
# 保修收集员
  "warranty_collector": {
  "prompt": WARRANTY_COLLECTOR_PROMPT,
  "tools": ["record_warranty_status"],
  "requires": [],
},
# 问题分类器
  "issue_classifier": {
  "prompt": ISSUE_CLASSIFIER_PROMPT,
  "tools": ["record_issue_status"],
  "requires": ["warranty_status"],
},
# 解决⽅案专家
  "resolution_specialist": {
  "prompt": RESOLUTION_SPECIALIST_PROMPT,
  "tools": ["resolve_in_warranty", "resolve_out_of_warranty"],
  "requires": ["warranty_status", "issue_type"],
},
}


#自定义所处步骤:"warranty_collector", "issue_classifier","resolution_specialist"
#本Agent支持的状态
SupportStep = Literal["warranty_collector", "issue_classifier",
"resolution_specialist"]
class HandoffsState(AgentState):
    current_step : NotRequired[SupportStep]
    warranty_status :NotRequired[Literal["in_warranty","out_of_warranty"]]
    issue_type :NotRequired[Literal["hardware","software"]]


#自定义工具
#1.修改当前“所处状态”的工具
#(1):将状态由“保修状态”-->“问题类型状态”
@tool
def record_warranty_status(
        warranty_state:Literal["in_warranty","out_of_warranty"],
        runtime:ToolRuntime[None,SupportStep]
)->Command:
    '''
    这是更改状态到“询问问题类型阶段“的工具，
    +记录下用户的保修状态
    '''
    return Command(
        update={"messages":[ToolMessage(
            content=f"保修记录已经更新为{warranty_state}",
            tool_call_id=runtime.tool_call_id
        )],
            "warranty_status": warranty_state,
            "current_step":"issue_classifier"
        },

    )

#(2):将状态由“问题类型状态”-->“解决问题状态”
@tool
def record_issue_status(
        issue_type:Literal["hardware","software"],
        runtime:ToolRuntime[None,SupportStep]
)->Command:
    '''
        这是更改状态到“给用户提供解决方案“的工具，
        +记录下用户的设备问题类型
    '''
    return Command(
        update={"messages":[ToolMessage(
            content=f"用户的设备问题类型已经更新为{issue_type}",
            tool_call_id=runtime.tool_call_id
        )],
            "issue_type": issue_type,
            "current_step":"resolution_specialist"
        }
    )


#2.提供解决方案的工具
#(1):当在“保修期”内的解决方案
@tool
def resolve_in_warranty(
        method:str
):
    '''为保修期用户直接提供解决方案'''
    return f"已经为用户提供了解决方案{method}"


#(2):当不在“保修期”内的解决方案
@tool
def resolve_out_of_warranty(
        reason:str,
):
    '''为不在保修期的用户，提升至“人工服务”解决问题'''
    return f"正在为用户接线人工服务，人工专家已知晓问题:{reason}"

#定义切换状态+调用每个状态方法的“中间件”
#名字 -> 工具对象 的映射
#request.override(tools=...) 需要真正的工具对象（BaseTool / Callable / 合法的 dict schema）；
#传字符串（工具名）会在 model 节点 bind_tools 时报
#"Functions must be passed in as Dict, pydantic.BaseModel, or Callable"
TOOL_MAP={
    record_warranty_status.name:record_warranty_status,
    record_issue_status.name:record_issue_status,
    resolve_in_warranty.name:resolve_in_warranty,
    resolve_out_of_warranty.name:resolve_out_of_warranty,
}

@wrap_model_call
def wrap_model_call(
        request:ModelRequest,
        handler:Callable[[ModelRequest],ModelResponse],
)->ModelResponse:
    '''根据当前步骤配置agent的行为'''
    #get用于“不确定是否为空”的情况，并且可以设置“默认值”
    #[]索引取值用于“确定一定不为空”的情况
    curent=request.state.get("current_step","warranty_collector")

    #查找当前状态的配置
    step_config=STEP_CONFIG[curent]

    #验证当前状态合理性
    #-->是否满足当前步骤的“前提条件”
    for key in step_config['requires']:
        if request.state.get(key) is None:
            raise ValueError(f"在进入步骤{step_config}之前，需要满足条件{key}")

    #提示词标准化注入
    system_prompt=step_config['prompt'].format(**request.state)

    # 注⼊系统提⽰词和步骤专⽤⼯具
    #不同状态继续进行下去/处于不同状态，工具+提示词都不同
    request = request.override(
        system_prompt=system_prompt,
        #STEP_CONFIG 里存的是工具名（字符串），要换回真正的工具对象
        tools=[TOOL_MAP[name] for name in step_config["tools"]],
    )
    return handler(request)


model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
#定义agent
agent=create_agent(
    model=model,
    tools=[record_warranty_status,record_issue_status,resolve_in_warranty,resolve_out_of_warranty],
    middleware=[
        SummarizationMiddleware(
            model=model,
            trigger=("tokens",4000),
            keep=("messages",20)
        ),
        wrap_model_call
    ],
    checkpointer=InMemorySaver(),  #用于多轮对话
    state_schema=HandoffsState,
)

config={"configurable":{"thread_id":"111"}}

result=agent.invoke(
    {"messages":[{"role":"user","content":"我的手机坏了"}]},
    config=config,
)

result=agent.invoke(
    {"messages":[{"role":"user","content":"是的，我的手机还在保修期内"}]},
    config=config,
)

result=agent.invoke(
    {"messages":[{"role":"user","content":"它的屏幕碎了"}]},
    config=config,
)

for message in result["messages"]:
    message.pretty_print()

