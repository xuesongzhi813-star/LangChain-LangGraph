import logging

from requests import session
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.common.exceptions import BusinessError
from app.models import Categories, Products
from app.schemas.product import ProductCreateRequest, ProductPageResponse, ProductUpdateRequest

logger = logging.getLogger(__name__)


def create_product(db: Session, payload: ProductCreateRequest) -> Products:
    name = payload.name.strip()
    # 先去掉首尾空白，再拒绝没有实际内容的商品名称。
    if not name:
        raise BusinessError("商品名称不能只包含空白")

    try:
        category = db.get(Categories, payload.category_id)
        # 正整数分类 ID 仍可能不存在，确认分类后才允许新增商品。
        if category is None:
            raise BusinessError("商品分类不存在")

        # **{"name": "可口可乐"} -> name="可口可乐", stock=100
        product = Products(**payload.model_dump())
        product.name = name
        db.add(product)
        db.commit()
        db.refresh(product)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("新增商品数据库操作失败")
        raise

    return product

def count_products(db:Session):
    '''查询数据库中有多少商品'''
    try:
        statement=select(func.count(Products.id))
        return db.scalar(statement)
    except SQLAlchemyError as e:
        logger.exception("统计商品数量失败")
        raise BusinessError("统计商品失败，请稍后重试",code=500) from e

def get_product(db:Session, product_id:int):
    '''按照product_id查询商品'''
    try:
        statement=select(Products).where(Products.id == product_id)
        return db.scalar(statement)
    except SQLAlchemyError as e:
        logger.exception("按照id查询商品失败")
        raise BusinessError("商品查询失败，请稍后重试",code=500) from e

#分页查询
def get_products(
       db:Session,
        keyword:str | None=None,
        category_id:int | None=None,
        page:int=1,
        page_size:int=10,
)->ProductPageResponse:
    #对其进行去除空白
    keyword=keyword.strip() if keyword else None
    filters=[]
    #有关键词才会进行搜素
    if keyword is not None:
        filters.append(Products.name.contains(keyword,autoescape=True))
    #只有提供分类ID才会筛选
    if category_id is not None:
        filters.append(Products.category_id == category_id)

    try:
        #查询商品有多少数量的语句-->应对category_id
        total_statement=select(func.count(Products.id)).where(*filters)
        total=db.scalar(total_statement)

        #分页查询
        statement=(
            select(Products).where(*filters)
            .order_by(Products.id.asc())
            .offset((page-1)*page_size)
            .limit(page_size)
        )
        items=db.scalars(statement).all()
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except SQLAlchemyError as e:
        logger.exception("查询商品列表失败，请稍后重试")
        raise BusinessError(code=500,message="查询商品列表失败，请稍后重试") from e


def update_product(
    db: Session,
    payload: ProductUpdateRequest,
    product_id: int,
) -> Products | None:
    '''更新商品属性'''
    try:
        product = db.get(Products, product_id)
        # 查不到商品时抛出业务异常，由全局处理器返回404。
        if product is None:
            raise BusinessError(message="未找到商品", code=404)
        changes = payload.model_dump(exclude_unset=True)
        # 一个字段都没有提交时没有可写入的内容，与第 04 节的规则一致。
        if not changes:
            raise BusinessError("至少提交一个需要修改的字段")
        for field, value in changes.items():
            # 显式提交的 null 表示要把字段清空，本项目的业务字段都不允许为空。
            if value is None:
                raise BusinessError(f"字段 {field} 的值不允许为 null")
        if "category_id" in changes:
            # 分类必须真实存在才能写入外键，先确认再保存，提示更明确。
            if db.get(Categories, changes["category_id"]) is None:
                raise BusinessError("商品分类不存在")
        for field, value in changes.items():
            # ORM 对象要逐个属性赋值，字典的 update() 不能用在对象上。
            # product: {"name": "矿泉水"} -> schema: {"name": "纯净水"}
            setattr(product, field, value)
        db.commit()
        db.refresh(product)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("修改商品数据库操作失败")
        raise
    return product

def delete_product(
        db:Session,
        product_id:int
):
    '''删除商品'''
    #先查询有无这个商品
    product=db.get(Products, product_id)

    #如果没有报错
    if product is None:
        raise BusinessError(code=404,message="要删除的商品不存在")

    #如果有则删除
    try:
        db.delete(product)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("删除失败")
        raise