from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ProductCreateRequest(BaseModel):
    category_id: int = Field(gt=0, description="所属分类ID")
    name: str = Field(min_length=1, max_length=50, description="商品名称")
    price: Decimal = Field(
        ge=0, decimal_places=2, max_digits=8, description="商品单价（元）"
    )
    stock: int = Field(default=0, ge=0, description="库存数量")
    shelf: bool = Field(default=True, description="是否上架")


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="商品ID")
    category_id: int = Field(description="所属分类ID")
    name: str = Field(description="商品名称")
    price: Decimal = Field(description="商品单价（元）")
    stock: int = Field(description="库存数量")
    shelf: bool = Field(description="是否上架")
    create_time: datetime = Field(description="创建时间")

    @field_serializer("price")
    def serialize_price(self, value: Decimal) -> str:
        return f"{value:.2f}"

    @field_serializer("create_time")
    def serialize_create_time(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")


class ProductCountResponse(BaseModel):
    '''查询有多少商品时，的返回格式'''
    total:int=Field(description="全部商品数量")

class ProductPageResponse(BaseModel):
    '''查询所有的商品，并且按照分页的方式返回'''
    items:list[ProductResponse]=Field(description="当前页商品")
    total:int=Field(description="符合条件的商品总数")
    page:int=Field(description="当前页码")
    page_size:int=Field(description="每页条数")

class ProductUpdateRequest(BaseModel):
    '''更新商品数据请求，请求的格式'''

    #模型校验时，去除字符串首尾空白
    ConfigDict(str_strip_whitespace=True)

    #因为修改属性，所有属性都是可选的
    category_id:int | None = Field(gt=0,description="商品种类",default=None)
    name:str | None =Field(min_length=1,max_length=50,default=None,description="商品名称")
    price:Decimal | None=Field(ge=0,default=None,description="商品金额，不超过2位小数",decimal_places=2,
        max_digits=8,)
    stock: int | None = Field(default=None, ge=0, description="库存，不小于0")
    shelf: bool | None = Field(default=None, description="上架状态")