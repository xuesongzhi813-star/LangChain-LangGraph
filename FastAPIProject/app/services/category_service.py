
"""
业务层代码：调用API后，要从API层到Service层
service层中才有处理业务的真正逻辑
"""
import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app.common.exceptions import BusinessError
from app.models import Categories
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
    try:
        db.add(category)   #插入数据
        db.commit()        #提交到数据库
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

