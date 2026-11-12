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