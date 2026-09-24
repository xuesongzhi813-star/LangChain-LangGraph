
from langgraph.graph import StateGraph, START
# 定义状态结构
class State(dict):
    topic: str
    joke: str

# 创建节点函数
def refine_topic(state):
    return {"topic": state["topic"] + "和猫"}

def generate_joke(state):
    return {"joke": f"这是⼀个关于{state['topic']}的笑话"}

# 构建图
graph = (
StateGraph(State)
.add_node(refine_topic)
.add_node(generate_joke)
.add_edge(START, "refine_topic")
.add_edge("refine_topic", "generate_joke")
.compile()
)
# 流式输出状态更新
# for chunk in graph.stream(
# {"topic": "冰激凌"},
# stream_mode="updates" # 只看更新部分
# ):
#     print(chunk)
    # {'refine_topic': {'topic': '冰激凌和猫'}}   所处节点名称+更新的状态值
    # {'generate_joke': {'joke': '这是⼀个关于冰激凌和猫的笑话'}}   所处节点名称+更新的状态值

for chunk in graph.stream(
{"topic": "冰激凌"},
stream_mode="values" # 每⼀步的完整状态
):
    print(chunk)
    # {'topic': '冰激凌'}  当前的节点的“所有状态值”
    # {'topic': '冰激凌和猫'}   当前的节点的“所有状态值”
    # {'topic': '冰激凌和猫', 'joke': '这是⼀个关于冰激凌和猫的笑话'}   当前的节点的“所有状态值”




















