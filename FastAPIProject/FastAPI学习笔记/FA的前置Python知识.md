

## Pydantic

Pydantic是借助“类”的形式，将一个“结构化”的数据示例，实现成一个带有“属性的类”，从而可以通过实例化对象去初始化

![alt text](assets/image.png)

## Annotated

Annotated是对一个函数内参数取值的**注入**  
可以理解为：当函数执行时，这个参数的取值，就是从Annotated注入中**可选取的列表**中选取出并且给参数赋值

![alt text](assets/image-1.png)

这里面name就是参数，后面“”中的就是**注入的元数据**

# 正式学习FastAPI

一个后来的理解：app更像是@注解的来源，要有这个对象才能调用注解

---
## 第一个接口的书写

### get接口的书写

![alt text](assets/image-2.png)

### FastAPI服务的启动

terminal中启动指令：
  - app.main:这个接口方法在app文件夹的main文件中
  - :app ：这个接口依赖的注册对象是app
```
uvicorn app.main:app --reload
```

### 关于在线测试你的接口

```
http://127.0.0.1:8000/docs
```

## 路径参数，查询参数与类型校验

### 路径参数

路径参数就是：“通过url传输接口方法所需的**参数**”

实现：“/”后使用“{}”传入与参数同名的数据
```
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

@app.get("/products/{product_id}")
def get_product(product_id: int):
    '''通过url中的路径参数，给接口参数传值'''
    for product in products:
        if product["id"] == product_id:
            return product
    return None
```
![alt text](assets/image-3.png)

### 固定路径与动态路径的补充

![
](assets/image-4.png)

其中count接口（固定路径）必须写在路径参数接口（动态路径：url不是固定的，因为传入了参数）前。  
否则，会造成count被解析成product_id的值，造成接口调用失败

### 查询参数

即借助url的Query String来传递参数

实现：直接在接口后加上"?page=1&page_size=2"
```
@app.get("/products")
def get_page_products(
        keyword: str | None = Query(max_length=100,description="按照关键词去模糊匹配查询"),
        page: int=Query(gt=0,default=1,description="查询商品的第几页"),
        page_size: int=Query(gt=0,default=5,description="当前页面最多展示多少")):
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

```

### 类型校验

可以限制“路径参数”和“查询参数”的取值范围等等，违反直接422报错

这里只用知道这些，其他可以查询官方文档：

1. Query针对查询参数，Path针对路径参数

2. gt是>，ge是>=，le是<=，lt是>

## 请求体作为参数（对象）

![alt text](assets/image-5.png)

```
@app.post("/products")
def read_product(payload: ProductCreate):
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
```
需要注意的几个点：

1. 请求体通过**Pydantic**的方式继承BaseModel作为**类**实现

2. 可以使用**Field**对类的**属性字段**进行限制，说明

3. 使用**model_dump()方法**可以实现“请求体”转换为JSON格式


## 引入状态码和修改，删除商品


## 与MySQL的交互（重点！！！）-->这里重点关注怎么连接

### 1. 与数据库交互的前置准备

#### 关于需要安装的依赖
![alt text](assets/image-6.png)

#### 配置MySQL数据库的配置信息文件--.env  
根目录下创建.env文件，内容配置如下：
```
DATABASE_URL=mysql+pymysql://root:2096867998@127.0.0.1:3306/fastapi_demo?charset=utf8mb4
```

#### 创造读取“环境变量”的示例对象  
在app文件夹下，创建config.py-->一般都是用于**读取本地环境中的配置资源**

```
from pydantic_settings import BaseSettings, SettingsConfigDict

'''
通过Settings对象读取环境变量中的配置信息
'''

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", #.env文件位置
        env_file_encoding="utf-8"  #.env文件内容数据格式
    )

    database_url: str

settings = Settings()
```

### 2. 正式创建

#### 定义engine和ORM基类

- engine：正式定义连接MySQL数据库

- ORM：ORM相当于是**对象关系映射**  
即：数据表-->映射成python类，表中的字段-->映射成类的属性

   - ORM基类：就是所有数据表中**都有的字段**，直接封装成一个**基类**，直接继承使用即可

   - ORM普通类：就是每个表格映射出的**python类**

---
engine与ORM基类：
```
from datetime import datetime

from sqlalchemy import create_engine, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

engine=create_engine(settings.database_url)

#ORM就是：将数据表-->映射成用python类表示，表中“属性字段（列）”-->python类中的属性
#ORM基类：后续表类都要继承的类
#通俗说法：所有表都有的公共字段，封装成公共类
class Base(DeclarativeBase):
    '''
    类中字段的理解：
    Mapped[int]：表中字段映射成类属性后，转换成python的基本数据类型
    mapped_column：表中该列，原本的“设置属性”是怎么样的
    '''
    id: Mapped[int] = mapped_column(
        Integer,primary_key=True,autoincrement=True,sort_order=-1,comment="主键ID"
    )

    create_time: Mapped[datetime] = mapped_column(
        DateTime,nullable=False,default=datetime.now,comment="创建时间"
    )
```
---

#### ORM普通类-->表格的映射
 ```
 
'''
编写两个ORM模型：商品分类表-->类，商品表-->类
'''
from decimal import Decimal

from sqlalchemy import String, Integer, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Categories(Base):
    '''
    __tablename__ ：由数据库中哪张表转换
    __table_args__：原本表的注释
    '''
    __tablename__ = 'categories'
    __table_args__ = {"comment": "商品分类表"}

    name: Mapped[str] = mapped_column(
        String(50),nullable=False,unique=True,comment="商品类别名"
    )

class Products(Base):
    __tablename__ = 'products'
    __table_args__ = {"comment": "商品表"}

    category_id: Mapped[int] = mapped_column(
        Integer,ForeignKey("categories.id"),nullable=False,comment="商品种类"
    )

    name: Mapped[str] = mapped_column(
        String(50),nullable=False,comment="商品名称"
    )

    price: Mapped[Decimal] = mapped_column(
        DECIMAL(8,2),nullable=False,comment="商品价格"
    )

    stock: Mapped[int] = mapped_column(
        Integer,nullable=False,default=0,comment="商品库存"
    )

    shelf: Mapped[bool] = mapped_column(
        Boolean,nullable=False,default=True,comment="商品是否上架"
    )

 ```

### 3.编写启动脚本

单独执行这个脚本，就能建表在MySQL中

```
from app import model
from app.database import Base, engine


#建表脚本
def main():
    """根据已经注册的模型，在数据库自动创建表"""
    print("开始执行创建表的脚本")
    Base.metadata.create_all(bind=engine)
    print("相关的表已经创建成功")

# 仅在主动运行此模块时建表，被其他模块导入时不执行。
if __name__ == "__main__":
    main()
```

## 真正与MySQL数据库操作（编写业务API）

接下来的板块就是实际编写后端服务器上API接口的工程板块

### models

专门存放**ORM映射的Python类**

例如这里映射了categories（商品种类表），product（商品表）

```
**关于商品种类表**

'''
model包的含义：一般存放ORM映射表->类后的类
ORM模型：商品分类表-->类.
'''
from decimal import Decimal

from sqlalchemy import String, Integer, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Categories(Base):
    '''
    __tablename__ ：由数据库中哪张表转换
    __table_args__：原本表的注释
    '''
    __tablename__ = 'categories'
    __table_args__ = {"comment": "商品分类表"}

    name: Mapped[str] = mapped_column(
        String(50),nullable=False,unique=True,comment="商品类别名"
    )
```

```
关于商品表

'''
model包的含义：一般存放ORM映射表->类后的类
ORM模型：商品表-->类
'''
from decimal import Decimal

from sqlalchemy import String, Integer, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Products(Base):
    __tablename__ = 'products'
    __table_args__ = {"comment": "商品表"}

    category_id: Mapped[int] = mapped_column(
        Integer,ForeignKey("categories.id"),nullable=False,comment="商品种类"
    )

    name: Mapped[str] = mapped_column(
        String(50),nullable=False,comment="商品名称"
    )

    price: Mapped[Decimal] = mapped_column(
        DECIMAL(8,2),nullable=False,comment="商品价格"
    )

    stock: Mapped[int] = mapped_column(
        Integer,nullable=False,default=0,comment="商品库存"
    )

    shelf: Mapped[bool] = mapped_column(
        Boolean,nullable=False,default=True,comment="商品是否上架"
    )
```
### schemas

一般schemas中存放调用API的**输入参数，封装成一个类**和**输出结果结构**-->这样前端可以清除接收API调用了什么，处理了什么
```
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

"""
结构化包装：
统一封装调用category表相关API，传入数据的格式/返回数据的格式
封装成类，方便调用。并且可以统一校验“参数问题”，不用一个个排查
"""


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="分类名称")


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="分类ID")
    name: str = Field(description="分类名称")
    create_time: datetime = Field(description="创建时间")

    @field_serializer("create_time")
    def serialize_create_time(self, value: datetime) -> str:
        # 2026-10-22 16:05:10
        return value.strftime("%Y-%m-%d %H:%M:%S")
```
### common

common中一般存放整个业务公用的内容：  
例如，统一返回结构，统一处理异常-->方便前后端交互，统一适配


### api

相当于Java中的controller层，暴露给前端的服务器后端API，但是只是调用，不是处理业务

### service
相当于Java中的service层，由api调用后进来处理业务逻辑


### main
这个层一般就是汇总所有的部分到一起，充当启动后的服务器
```

"""
最终统一的服务器
"""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api import api_router
from app.common.exceptions import BusinessError, handle_business_error, handle_database_error, handle_http_error, \
    handle_validation_error, handle_unexpected_error
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.common.response import Response

#统一接口返回（调用失败的统一返回）
app = FastAPI(responses={422: {"model": Response,"description": "请求参数校验失败"}})
#所有分支路由，汇总到总路由
app.include_router(api_router)

#汇总所有的异常处理
app.add_exception_handler(BusinessError, handle_business_error)
app.add_exception_handler(SQLAlchemyError, handle_database_error)
app.add_exception_handler(StarletteHTTPException, handle_http_error)
app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(Exception, handle_unexpected_error)


@app.get("/")
def read_root():
    '''观测FastAPI服务器是否存活'''
    return {"message": "FastAPI服务器正在运行中"}



```