import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
#创建应用对象，后续使用app对象注册接口
app=FastAPI()

categories = [
    {"id": 1, "name": "饮料", "create_time": "2026-10-13 08:00:00"},
    {"id": 2, "name": "数码配件", "create_time": "2026-10-13 08:00:00"},
    {"id": 3, "name": "零食", "create_time": "2026-10-13 08:00:00"},
]

products = [
    {
        "id": 1,
        "category_id": 1,
        "name": "矿泉水",
        "price": "3.50",
        "stock": 100,
        "shelf_status": True,
        "create_time": "2026-10-13 09:00:00",
    },
    {
        "id": 2,
        "category_id": 1,
        "name": "可乐",
        "price": "5.00",
        "stock": 80,
        "shelf_status": True,
        "create_time": "2026-10-13 10:00:00",
    },
    {
        "id": 3,
        "category_id": 2,
        "name": "USB 数据线",
        "price": "19.90",
        "stock": 0,
        "shelf_status": False,
        "create_time": "2026-10-13 11:00:00",
    },
]

class ProductCreate(BaseModel):
    '''
    描述新增商品时，客户端可以提交的字段

    同时引入Filed进行字段取值的约束（类似对“查询参数”/“路径参数”的约束）：
    如果必须满足的约束并没有完成，就会422报错
    '''
    category_id: int | None=Field(default=None,gt=0,description="商品种类的分类id，必须填写")
    name: str | None=Field(default=None,min_length=1,max_length=50,description="商品名称，必须填写")
    price: Decimal | None=Field(default=None,gt=0,description="商品的价格，必须填写")
    stock: int | None=Field(default=None,ge=0,description="商品库存")
    shelf_status: bool | None=Field(default=None,description="商品的上架状态")

@app.get("/")
def first_api():
    '''不接收数据，只是返回json格式的数据回去'''
    return {"message": "FastAPI running"}

@app.get("/hello")
def hello_world():
    return {"message": "Hello World"}


###################接收的是“基本数据”类型#################################

@app.get("/products/count")
def get_product():
    '''获取到当前订单商品列表的长度'''
    return {
        "length": len(products),
    }

#补充查找不到商品的情况-->重载函数
def get_product_or_404(product_id:int):
    '''这里重构封装了“获取商品”的方法。解决应对了找到/找不到的情况。共用一个路径接口，而非两个url'''
    product=next((item for item in products if item["id"] == product_id),None)
    #如果查找不到404异常
    if product is None:
        raise HTTPException(status_code=404,detail="商品不存在")
    return product

@app.get("/products/{product_id}")
def get_product(product_id:Annotated[int,Path(gt=0)]):
    '''通过url中的路径参数，给接口参数传值'''
    return get_product_or_404(product_id)

@app.get("/products")
def get_page_products(
        keyword: Annotated[str | None , Query(max_length=100,description="按照关键词去模糊匹配查询")] = None,
        page: Annotated[int,Query(gt=0,description="查询商品的第几页")] = 1,
        page_size: Annotated[int,Query(gt=0,description="当前页面最多展示多少")] = 5):
    '''通过url中的query string（查询参数），动态给接口参数传值
    适用于：本方法（页面显示信息，动态改变的）
    '''
    filter_products=products
    #如果存在关键词查询
    if keyword and keyword.strip():
        '''这里就要根据关键词，去模糊查询，更新products数组'''
        filter_products=[]
        for product in products:
            if keyword.strip().lower() in product.get("name").lower():
                filter_products.append(product)
    start=(page-1)*page_size
    end=start+page_size
    return {
        "items": filter_products[start:end],
        "page": page,
        "page_size": page_size,
        "total_count": len(filter_products),
    }


#删除某个商品
@app.delete("/products/{product_id}")
def delete_product(product_id:int):
    '''根据商品id删除商品'''
    product=get_product_or_404(product_id)
    products.remove(product)
    return {"message": "商品删除成功"}

########################JSON格式的数据传递（请求体/对象）#########################
@app.post("/products")
def create_product(payload: ProductCreate):
    """
    接收商品新增的数据，暂时先返回校验后数据

    在正式新增前，进行参数校验；校验成功则拼接上products数组中
    """
    name = payload.name.strip()

    if not name:
        raise HTTPException(status_code=400, detail="商品名称不能为空")
    # id_exists = False
    # for category in categories:
    #     if payload.category_id == category["id"]:
    #         id_exists = True
    #         break
    # if not id_exists:
    #     raise HTTPException(status_code=400, detail="分类ID不存在")
    if not any(payload.category_id == category["id"] for category in categories):
        raise HTTPException(status_code=400, detail="分类ID不存在")

    payload.name = name
    # 新增商品  我们需要从商品列表里找到最大的ID  再 +1 变成新的商品ID
    next_id = max((product["id"] for product in products), default=0) + 1
    payload.model_dump()
    # **dict 放到了 ProductCreate(**dict) -> name="矿泉水", price=2.23
    # **{"name": "矿泉水"} -> {"name": "矿泉水"}
    product = {
        "id": next_id,
        **payload.model_dump(),
        "create_time": datetime.now(timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }  # UTC +8
    products.append(product)
    return product

#关键是：学会知道“patch”是用来修改“部分数据”
@app.patch("/products/{product_id}")
def update_product(payload: ProductCreate, product_id: int = Path(gt=0)):
    """接收商品修改字段的数据，更新对应的商品字段数据  返回修改后的商品数据"""
    # 确认商品是否存在
    product = get_product_or_404(product_id)
    # 看下本次提交的数据有无新增的字段需要改动
    changes = payload.model_dump(exclude_unset=True)  # {"name": null} -> {}
    if not changes:
        raise HTTPException(status_code=400, detail="至少提交一个需要修改的字段")

    for field, value in changes.items():
        if value is None:
            # 判断客户端是否提交了 值为None 的字段
            raise HTTPException(
                status_code=400, detail=f"字段 {field} 的值不允许为 null"
            )
    if "name" in changes:
        changes["name"] = changes["name"].strip()  # ""
        if not changes["name"]:
            raise HTTPException(status_code=400, detail="商品名称不能为空")
    if "category_id" in changes:
        if not any(category["id"] == changes["category_id"] for category in categories):
            raise HTTPException(status_code=400, detail="商品分类不存在")
    product.update(changes)  # 按照 key 来进行覆盖  {"name": "巧克力", "stock" : 100}
    return product