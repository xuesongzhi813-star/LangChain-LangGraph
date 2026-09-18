import operator
from typing import TypedDict, Annotated

from langgraph.constants import START, END
from langgraph.graph import StateGraph


#这是一个学习LangGraph如何构建图的demo
#1.定义状态
class PackageState(TypedDict):
    '''定义包裹的状态'''
    id:str
    origin_site:str #起始地
    destination_site:str #收货地

    '''定义配送状态'''
    status:str #配送时状态
    history:Annotated[list[str],operator.add] #可拼接更新，历史流程
    total_mileage:Annotated[int,operator.add] #可拼接更新，总里程数

    '''定义配送详情'''
    delivery_method:str #加急/普通

#2.定义节点（本质函数，输入：状态，输出：更新状态）
#定义“揽收节点”
def Collection_point(
        state: PackageState,
):
    '''揽收点，更新包裹状态+历史记录'''
    return {
        "status": "已揽收",
        "history": [f"在{state['origin_site']}被站点揽收"]
    }

#定义分拣节点
def Sorting_station(
  state: PackageState,
):
    '''根据目的地，来分拣'''
    destination=state["destination_site"]
    if destination == "北京":
        order_site="北京"
    elif destination == "上海":
        order_site="上海"
    else:
        order_site="其他地区"
    return {
        "status": "运输中",
        "history": [f"分拣完毕，即将送至{order_site}分拣站"]
    }

#定义派送站节点
def Delivery_station(
  state: PackageState,
):
    '''派送包裹'''
    return {
        "status": "派送中",
        "history": [f"正在{state['destination_site']}本地派送中"]
    }

#定义标准配送节点
def Ordinary_transport(
        state: PackageState,
):
    '''普通运输的节点状态配置'''
    return {
        "total_mileage": 500,
        "status": "陆运运输",
        "history": ["陆运运输"]
    }

#定义加急运输节点
def Express_transport(
    state: PackageState,
):
    '''加急运输的节点状态配置'''
    return {
        "total_mileage": 800,
        "status": "空运加急运输",
        "history": ["空运加急运输"]
    }

#3.定义图
delivery=StateGraph(PackageState)

#4.添加节点
delivery.add_node("揽收站",Collection_point)
delivery.add_node("分拣点",Sorting_station)
delivery.add_node("派送站",Delivery_station)
delivery.add_node("普通运输",Ordinary_transport)
delivery.add_node("加急运输",Express_transport)

#分拣条件判断方法
def decide_transport_method(
        state: PackageState,
):
    method=state["delivery_method"]
    if method == "普通":
        return "普通"
    elif method == "加急":
        return "加急"
    else:
        return "普通"

dic={
    "普通":"普通运输",
    "加急":"加急运输"
}

#5.添加边
delivery.add_edge(START,"揽收站") #固定边
delivery.add_edge("揽收站", "分拣点") #固定边
delivery.add_conditional_edges("分拣点",decide_transport_method,dic) #条件边
delivery.add_edge("普通运输","派送站") #固定边
delivery.add_edge("加急运输","派送站") #固定边
delivery.add_edge("派送站",END) #固定边

#6.编译图
delivery_system=delivery.compile()

#7.测试
test_packages = [
{
"id": "P001",
"origin_site": "北京",
"destination_site": "上海",
"delivery_method": "普通",
"history": [],
"total_mileage": 0
},
{
"id": "P002",
"origin_site": "⼴州",
"destination_site": "乌鲁⽊⻬",
"delivery_method": "加急",
"history": [],
"total_mileage": 0
}
]
for package in test_packages:
    print(f"\n配送包裹: {package['id']}")
    result = delivery_system.invoke(package)
    print("最终状态:", result["status"])
    print("配送历史:", result["history"])
    print("总⾥程:", result["total_mileage"])








