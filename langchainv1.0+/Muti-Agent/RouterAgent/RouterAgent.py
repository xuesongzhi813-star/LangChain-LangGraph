import operator
import os
from typing import TypedDict, Annotated, List

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    extra_body={"thinking": {"type": "disabled"}}, #关闭思考模式->使用结构化输出
)

#agent节点之间的传递状态
class AgentInput(TypedDict):
    '''传递给子Agent的私有状态'''
    query: str  #输入

class AgentOutput(TypedDict):
    '''子Agent节点传给“总结”节点的私有状态'''
    result: str  #输出结果
    source:str  #输出来源

#路由到子Agent节点传输的私有状态
class Classification(TypedDict):
    '''私有状态'''
    source:str  #路由到哪个节点agent
    query: str  #路由到节点的请求参数

#图状态
class State(TypedDict):
    query:str  #输入请求
    classification:List[Classification]  #分类节点的输出状态
    results:Annotated[List[AgentOutput],operator.add]  #输出结果集合
    final_answer:str  #最终输出

####################### 定义节点##################################

class RouteStructural(BaseModel):
    """用户分类查询结果的结构"""
    classifications: list[Classification] = Field(
        description="要调用的Agent列表以及其针对性的子问题"
    )
#定义路由问题的节点
def route_query(state:State):
    '''使用LLM结构化输出实现（DeepSeek不支持response_format=json_schema，改用function_calling）'''
    with_struct_model = model.with_structured_output(RouteStructural, method="function_calling")
    struct_result=with_struct_model.invoke(
        [SystemMessage(content="""分析此查询，确定需要咨询哪些知识库。为每个相关来源生成一个针对该来源优化的子问题。
可用来源：
- github: 代码， API参考， 实现细节， Issue， Pull Request
- notion: 内部文档， 流程， 策略， 团队Wiki
- slack: 团队讨论， 非正式知识分享， 近期对话
只返回与查询相关的来源。"""),HumanMessage(content=state["query"])]
    )
    return {
        "classification": struct_result.classifications,
    }


# GitHub 工具
@tool
def search_code(query: str, repo: str = "main") -> str:
    """在GitHub仓库中搜索代码。"""
    return f"在{repo}库中找到匹配'{query}'的代码：src/auth.py中的认证中间件"

@tool
def search_issues(query: str) -> str:
    """搜索GitHub issues和pull requests。"""
    return f"找到3个匹配'{query}'的Issue：#142 (API认证文档), #89 (OAuth流程), #203 (令牌刷新)"

@tool
def search_prs(query: str) -> str:
    """搜索实现细节相关的PR。"""
    return f"PR #156: 新增JWT认证，PR #178: 更新OAuth作用域"

# Notion 工具
@tool
def search_notion(query: str) -> str:
    """在Notion工作区搜索文档。"""
    return f"找到文档：'API认证指南' - 涵盖OAuth2流程、API密钥和JWT令牌"

@tool
def get_page(page_id: str) -> str:
    """通过ID获取特定Notion页面。"""
    return f"页面内容：分步认证设置说明"

# Slack 工具
@tool
def search_slack(query: str) -> str:
    """搜索Slack消息和讨论串。"""
    return f"在#engineering频道发现讨论：'API认证使用Bearer令牌，刷新流程见文档'"

@tool
def get_thread(thread_id: str) -> str:
    """获取特定Slack讨论串。"""
    return f"讨论串中涉及API密钥轮换的最佳实践"


github_agent = create_agent(
    model,
    tools=[search_code, search_issues, search_prs],
    system_prompt=(
        "你是GitHub专家。通过搜索仓库、Issue和PR，"
        "回答关于代码、API参考和实现细节的问题。"
    ),
)

notion_agent = create_agent(
    model,
    tools=[search_notion, get_page],
    system_prompt=(
        "你是Notion专家。通过搜索组织的Notion工作区，"
        "回答关于内部流程、策略和团队文档的问题。"
    ),
)

slack_agent = create_agent(
    model,
    tools=[search_slack, get_thread],
    system_prompt=(
        "你是Slack专家。通过搜索相关讨论串，"
        "回答团队成员分享过知识和解决方案的问题。"
    ),
)


def query_github(state: AgentInput):
    """调用github专家Agent并返回结果"""

    github_result = github_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    return {"results": [{"source": "github", "result": github_result["messages"][-1].content}]}

def query_notion(state: AgentInput):
    """调用notion专家Agent并返回结果"""
    notion_result = notion_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    return {"results": [{"source": "notion", "result": notion_result["messages"][-1].content}]}


def query_slack(state: AgentInput):
    """调用slack专家Agent并返回结果"""
    slack_result = slack_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    return {"results": [{"source": "slack", "result": slack_result["messages"][-1].content}]}

#总结结果节点
def summary_node(state:State):
    """将所有Agent的结果合成一个连贯的回答。"""
    if not state["results"]:
        return {"final_answer": "未从任何知识源找到结果"}

    formatted = [
        f"**来自{r["source"]}: **\n{r["result"]}"
        for r in state["results"]
    ]

    synthesis_result = model.invoke([
        {"role": "system", "content": f"""请综合以下搜索结果回答原始问题: "{state['query']}"
    - 合并多个来源的信息，避免冗余
    - 突出最相关、最具可操作性的信息
    - 注意来源间的差异
    - 保持回答简洁且组织良好"""},
        {"role": "user", "content": "\n\n".join(formatted)}
    ])
    return {"final_answer": synthesis_result.content}

#根据查询结果，跳转到不同的agent节点（路由的实现）
def route(state:State):
    return [
        Send(c["source"], {"query": c["query"]}) for c in state["classification"]
    ]


builder=StateGraph(State)
builder.add_node(route_query)
builder.add_node(summary_node)
builder.add_node("github",query_github)
builder.add_node("notion",query_notion)
builder.add_node("slack",query_slack)

builder.add_edge(START,"route_query")
builder.add_conditional_edges("route_query",route,["github","notion","slack"])
builder.add_edge("github","summary_node")
builder.add_edge("notion","summary_node")
builder.add_edge("slack","summary_node")
builder.add_edge("summary_node",END)

graph=builder.compile(checkpointer=InMemorySaver())

config={"configurable":{"thread_id":"111"}}
result=graph.invoke({"query":"如何认证API请求"},config=config)
print("最终结果为:" + result["final_answer"])




















