"""
这里相当于是Java中的controller
将接口统一封装在一个包中调用
业务处理到service包中
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common import response
from app.dependencies import get_db
from app.schemas.category import CategoryCreateRequest, CategoryResponse
from app.services import category_service

#类似app=FastAPI()实例化对象，从而使用@注解
"""
prefix:前缀，相当于"/后的内容"，后面@中就不用加具体url了
tags：给这个文件中接口分类标签
"""
category_router=APIRouter(prefix="/categories",tags=["商品分类相关的接口"])


"""
response_model:统一返回格式
payload:接口调用所需参数封装的“类型”
Session=Depends（）：相当于Java中@Autowired注入单例的“数据库”对象
model_validate：ORM对象校验参数
"""
@category_router.post("", response_model=response.Response)
def create_category(payload: CategoryCreateRequest,db: Session=Depends(get_db)):
    return response.Response.success(
        data=CategoryResponse.model_validate(
            category_service.create_category(db,payload)
        )
    )

