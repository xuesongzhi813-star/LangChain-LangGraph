from typing import Any

from pydantic import BaseModel

'''
调用后端API的结果，返回结果被包装成“统一格式”返回-->成功/失败
相当于SpringBoot的封装Result
这里的Any类型的data，相当于是Java中T，可以接收传的“自定义独特业务”的“请求体”
'''

class Response(BaseModel):
    """API层统一返回的数据对象"""

    code: int
    message: str
    data: Any = None


    '''
    根据“调用成功与否”，调用方法返回结果，不需要实例化Response对象配置！！！
    相当于static，将此方法归为类，作为类方法。
    直接Response.success（）调用
    '''


    @classmethod
    def success(cls, data: Any = None, message: str = "请求成功"):
        # {"code": 200, message: "请求成功", data=None}
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: Any = None):
        # {"code": 500, message: "商品的名称唯一", data=None}
        return cls(code=code, message=message, data=data)