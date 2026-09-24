'''在“线程级持久化”的形式下，使用“第三方存储库”实现持久化'''
import os

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph

model=ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

#定义节点
def node(
        state:MessagesState
):
    '''正常调用AI'''
    result=model.invoke(state["messages"])
    return {
        "messages":result
    }

#定义图，添加节点，添加边
builder=StateGraph(MessagesState)

builder.add_node(node)

builder.add_edge(START,"node")
builder.add_edge("node",END)

#通过Postgres数据库，完成持久化
DB_URI = "postgresql://postgres:2096867998@81.71.3.45:5432/postgres"
#注意：with代码块退出时会关闭数据库连接，所以编译和调用图的操作必须放在with块内部
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    # 第⼀次使⽤ Postgres 检查点时需要调⽤ checkpointer.setup()
    checkpointer.setup()

    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "1"}}
    response = graph.invoke({"messages": [{"role": "user", "content": "你好，我是小明"}]},
                            config)
    response["messages"][-1].pretty_print()

    result = graph.invoke({"messages": [{"role": "user", "content": "刚才我们聊了什么？"}]},
                          config)
    result["messages"][-1].pretty_print()

    #打印所有的工作流消息
    print(result["messages"])
#这里会记录下6个“状态快照”：
#第一个START之前-->第二个START之后，node节点之前-->第三个node结束之后，END之前
#第四，五，六个同上-->因为是执行了两个工作流，步骤都一样









