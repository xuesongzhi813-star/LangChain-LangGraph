from typing import Optional

from pydantic import BaseModel, Field

class ReserveList(BaseModel):
    '''预定过的房源的基本信息'''
    order_id:str=Field(default=None,description="（预定的这一单）工单id")
    house_name:str=Field(default=None,description="预定的房源名称")
    order_phone:str=Field(default=None,description="预定的电话号码")
    price:Optional[str]=Field(default=None,description="该房源的价位")
    house_info:Optional[str]=Field(default=None,description="该房源的基本信息介绍")
    city:Optional[str]=Field(default=None,description="房源所在的城市")
    region:Optional[str]=Field(default=None,description="房源所在的详细区域")

class UserPreference(BaseModel):
    '''用户的偏好信息'''
    '''
    Optional用于设置该变量是“可选的”，不是必须的
    Field用于设置“默认值”+“描述”
    '''
    max_budget:Optional[float]=Field(default=None,description="用户的最高预算值")
    min_budget:Optional[float]=Field(default=None,description="用户的最低预算值")
    reserve_list:Optional[list[ReserveList]]=Field(default=None,description="已经预定过的房源列表")



