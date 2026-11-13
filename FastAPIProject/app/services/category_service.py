
"""
业务层代码：调用API后，要从API层到Service层
service层中才有处理业务的真正逻辑
"""
import logging

from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app.common.exceptions import BusinessError
from app.models import Categories, Products
from app.schemas.category import CategoryCreateRequest

logger=logging.getLogger(__name__)

"""
定义创建新的商品种类的“业务处理逻辑”
"""
def create_category(db: Session,payload: CategoryCreateRequest)->Categories:
    name=payload.name.strip()
    #去除首尾空白后不能没有内容，否则分类就缺失“名称”
    if not name:
        raise BusinessError("分类名称不能为空！")

    category=Categories(name=name)  #实例化一个Categories类对象
    #这里本质是一个mysql事务操作
    try:
        db.add(category)   #提交到session暂存
        db.commit()        #提交事务到数据库
        db.refresh(category)   #更新最新数据
    except SQLAlchemyError as e:
        db.rollback()   #如果遇到错误，则回滚操作
        logger.error("新增分类数据库操作失败")
        #分类名有唯一约束，则这里将“异常”详细化处理，而不是统一exception
        #原因：一般都是因为插入数据已经存在，才会抛出异常，很少是服务器方面
        #这里Exception相当于兜底异常处理（应对服务器）
        #进入之后，再详细判断是不是“重名插入失败”
        if isinstance(e,IntegrityError) and e.orig.args[0]==1062:
            raise BusinessError("分类名已存在",code=409) from e
        raise
    return category

'''
定义查询所有商品类别API的业务逻辑
'''
def read_categories(db: Session):
    '''查询所有的商品分类'''
    try:
        '''
        书写查询语句：
        1.要查询的列-->已经被映射封装到类中，直接查询类
        2.要借助db（session操作的当前数据库）去scalars执行查询
        '''
        statement=select(Categories).order_by(Categories.id.asc())
        return db.scalars(statement).all()
    except SQLAlchemyError as e:
        logger.exception("查询商品分类失败")
        raise BusinessError(code=500,message="查询分类失败，稍后重试") from e

def update_category(
    db: Session, payload: CategoryCreateRequest, category_id: int
) -> Categories:
    category = db.get(Categories, category_id)
    if not category:
        raise BusinessError(message="分类不存在", code=404)
    try:
        statement=update(Categories).where(Categories.id == category_id).values(name=payload.name)
        db.commit()
        db.refresh(category)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("修改分类数据库操作失败")
        # 分类名有唯一约束，仅 MySQL 1062 表示这里的重名冲突。
        if isinstance(exc, IntegrityError) and exc.orig.args[0] == 1062:
            raise BusinessError("分类名称已存在", code=409) from exc
        raise

    return category


def delete_category(db: Session, category_id: int):
    category = db.get(Categories, category_id)
    if category is None:
        raise BusinessError(message="分类不存在", code=404)
    # 按商品所属分类统计，不能把商品主键当成分类外键。
    product_count = db.scalar(
        select(func.count(Products.id)).where(Products.category_id == category_id)
    )
    if product_count > 0:
        raise BusinessError(message="分类下有其他商品，不能删除分类", code=409)
    try:
        db.delete(category)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("删除分类数据库操作失败")
        raise