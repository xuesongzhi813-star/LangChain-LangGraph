from langchain_core.tools import tool



#“订单查询”工具(异步，支持并行)

#定义类，一个订单应该有哪些属性


@tool
async def query_order()->list[str]:
    '''根据手机号/用户订单号，查询得到用户的所有订单列表'''






