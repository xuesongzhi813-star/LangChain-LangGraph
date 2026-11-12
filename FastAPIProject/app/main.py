
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

















