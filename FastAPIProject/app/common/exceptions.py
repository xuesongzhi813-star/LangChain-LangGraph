import logging

from fastapi import Request, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.response import Response


#自定义异常类型
class BusinessError(ValueError):
    """可向客户端说明的业务错误，默认返回400。"""

    def __init__(self, message: str, code: int = 400):
        self.code = code
        super().__init__(message)

#日志类，类似Java中的Sl4j，直接打印不同的日志
logger = logging.getLogger(__name__)

app=FastAPI()


'''
统一处理异常：
发生不同异常时，就会根据“异常类型”走对应的返回格式和处理方式
'''
@app.exception_handler(BusinessError)
def handle_business_error(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=exc.code,
        content=Response.error(code=exc.code, message=str(exc)).model_dump(mode="json"),
    )

@app.exception_handler(SQLAlchemyError)
def handle_database_error(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content=Response.error(
            code=500, message="数据库操作失败，请检查记录后重试"
        ).model_dump(mode="json"),
    )

@app.exception_handler(StarletteHTTPException)
def handle_http_error(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=Response.error(code=exc.status_code, message=exc.detail).model_dump(
            mode="json"
        ),
        headers=exc.headers,
    )

@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=Response.error(
            code=422,
            message="请求参数校验失败",
            data=jsonable_encoder(exc.errors()),
        ).model_dump(mode="json"),
    )

@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception):
    logger.error("处理请求时发生未预期异常", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=Response.error(code=500, message="服务器内部错误").model_dump(
            mode="json"
        ),
    )