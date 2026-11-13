from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends, Path,Query
from sqlalchemy.orm import Session, Query
from fastapi import FastAPI, Path, Query, HTTPException
from app.common.response import Response
from app.dependencies import get_db
from app.schemas.product import ProductCreateRequest, ProductResponse, ProductCountResponse, ProductPageResponse, \
    ProductUpdateRequest
from app.services import product_service

product_router=APIRouter(prefix="/products",tags=["商品相关接口"])

@product_router.post("",
                     response_model=Response,
                     summary="新增商品",
                     description="接收商品资料，校验所属分类存在后创建商品，并返回生成的ID、创建时间等完整信息。",)
def create_category(payload:ProductCreateRequest,db:Session=Depends(get_db)):
    return Response.success(
        data=ProductResponse.model_validate(
            product_service.create_product(db,payload)
        )
    )

#先完成统计商品数量+按照id查询商品的接口
@product_router.get("/count",response_model=Response,
                    summary="统计商品总数",
                    description="统计全部商品数量，不应用商品列表接口的关键词和分类筛选条件。",
                    )
def count_products(db:Annotated[Session,Depends(get_db)]):
    return Response.success(
        data=ProductCountResponse(
            total=product_service.count_products(db)
        )
    )

@product_router.get("/{product_id}",
                    response_model=Response,
                    summary="查询商品详情",
                    description="根据正整数商品ID查询商品详情；商品不存在时返回404。",)
def get_product(db:Annotated[Session,Depends(get_db)],product_id:Annotated[int,Path(gt=0)]):
    product = product_service.get_product(db, product_id)
    # 合法的正整数不一定有对应记录，没有商品时返回404而不是200和null。
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return Response.success(data=ProductResponse.model_validate(product))

@product_router.get("",response_model=Response,
                    summary="分页模糊查询商品数据",
                    description="支持按名称关键词和分类ID组合筛选，按商品ID倒序分页，返回当前页商品与筛选后的商品总数"
                    )
def get_products(
        db:Annotated[Session,Depends(get_db)],
        keyword:Annotated[int | None,Query(max_length=50,description="关键词模糊查询")]=None,
        category_id:Annotated[int | None,Query(gt=0,description="商品种类")]=None,
        page:Annotated[int,Query(ge=1,description="查询页码")]=1,
        page_size:Annotated[int,Query(ge=1,le=100,description="每页显示消息条数")]=10
):
    return Response.success(
        data=ProductPageResponse.model_validate(
            product_service.get_products(db,keyword,category_id,page,page_size)
        )
    )

@product_router.patch("/{product_id}",
                      response_model=Response,
                      summary="修改商品",
                      description="按商品ID局部修改商品，只更新提交的字段；修改成功返回完整商品，不存在时返回404。",
                      )
def update_product(
        db:Annotated[Session,Depends(get_db)],
        payload:ProductUpdateRequest,
        product_id:Annotated[int,Path(gt=0)],
):
    '''更新商品'''
    return Response.success(
        data=ProductResponse.model_validate(
            product_service.update_product(db,payload,product_id)
        )
    )


@product_router.delete("/{product_id}",
                       response_model=Response,
                       summary="删除商品",
                       description="按商品ID删除一条记录；不存在时返回404，删除成功返回统一成功响应。",
                       )
def delete_product(
        db:Annotated[Session,Depends(get_db)],
        product_id:Annotated[int,Path(gt=0)]
):
    '''删除商品'''
    product_service.delete_product(db,product_id)
    return Response.success()
