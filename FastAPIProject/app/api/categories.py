"""
这里相当于是Java中的controller
将接口统一封装在一个包中调用
业务处理到service包中
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.common.response import Response
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
summary：接口的基本摘要
description：接口返回的详细信息
payload:接口调用所需参数封装的“类型”
Session=Depends（）：相当于Java中@Autowired注入单例的“数据库”对象--》一般推荐Annotated[Session,Depends(get_db)]]写法
model_validate：ORM对象校验参数
"""
@category_router.post("", response_model=Response,
                      summary="创建新的商品类型",
                      description="创建新的商品类型的API接口，创建成功返回分类详情，创建失败409异常（一般是重名）")
def create_category(payload: CategoryCreateRequest,db: Session=Depends(get_db)):
    return response.Response.success(
        data=CategoryResponse.model_validate(
            category_service.create_category(db,payload)
        )
    )

@category_router.get("", response_model=Response,
                     responses={500: {"model": Response, "description": "查询分类失败，返回500服务器异常"}},
                     summary="查询现有的商品类型",
                     description="查询现在所有的商品类型，成功则返回类型列表，失败则返回500服务器异常")
def read_categories(db:Annotated[Session,Depends(get_db)]):
    return response.Response.success(
        data=[CategoryResponse.model_validate(item)
            for item in category_service.read_categories(db)
              #返回的是[]列表
    ])

@category_router.patch(
    "/{category_id}",
    response_model=Response,
    summary="修改分类名称",
    description="按分类ID修改名称并返回分类信息；重名时返回409，不存在时返回404。",
)
def patch_category(
    payload: CategoryCreateRequest,
    category_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
):
    # 分类对象通过响应模型处理，沿用已有字段和时间序列化规则。
    return Response.success(
        data=CategoryResponse.model_validate(
            category_service.update_category(db=db, payload=payload, category_id=category_id)
        )
    )


@category_router.delete(
    "/{category_id}",
    response_model=Response,
    summary="删除商品分类",
    description="仅删除没有商品的分类；有商品时返回409，不存在时返回404，成功返回统一成功响应。",
)
def delete_category(
    category_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
):
    category_service.delete_category(db=db, category_id=category_id)
    return Response.success()