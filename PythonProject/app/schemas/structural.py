from typing import Literal

from pydantic import BaseModel, Field,field_validator
from enum import Enum

class ExtractRequest(BaseModel):
    text: str = Field(min_length=1, description="用户的售后描述原文")

#模型的结构化输出
#关于“售后咨询”的结构化输出
#用户“售后咨询”，可能出现的类型
class RequestType(str, Enum):
    REFUND = "退款"
    EXCHANGE = "换货"
    REPAIR = "维修"
    COMPLAINT = "投诉"
    OTHER = "其他"

#另一种写法-->这种写法适配于“结构化输出”供给模型选择，因此，这里不适用
# class RequestType(BaseModel):
#     actions:Literal["退款","换货","维修","投诉","其他"]

class AfterSaleTickets(BaseModel):
    '''从用户售后描述中提取出结构化的工单'''
    order_id:str|None=Field(
        default=None,
        description="原文中出现的订单号，如果没有找到则默认为None，禁止编造一个订单号"
    )
    request_type:RequestType=Field(description="用户的售后需求类型，可以从原文中总结提取出")
    expected_solution:str=Field(description="用户提出的期望处理结果，尽量总结成1到2句话概述")

    @field_validator("order_id", mode="before")
    @classmethod
    def _normalize_missing_order_id(cls, v: object) -> object:
        # LLM没有在原文中提取到“工单号”：期望：不传参数，实际：可能会传null/无，导致占位符，
        #设置before就是在进行结构化之前，校验，统一成None
        if isinstance(v, str) and v.strip().lower() in {"", "null", "none", "n/a", "无"}:
            return None
        return v







