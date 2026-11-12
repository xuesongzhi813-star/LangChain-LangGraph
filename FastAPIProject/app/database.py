from datetime import datetime

from sqlalchemy import create_engine, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import settings

engine=create_engine(settings.database_url)

SessionLocal = sessionmaker(bind=engine)

#ORM就是：将数据表-->映射成用python类表示，表中“属性字段（列）”-->python类中的属性
#ORM基类：后续表类都要继承的类
#通俗说法：所有表都有的公共字段，封装成公共类
class Base(DeclarativeBase):
    '''
    类中字段的理解：
    Mapped[int]：表中字段映射成类属性后，转换成python的基本数据类型
    mapped_column：表中该列，原本的“设置属性”是怎么样的
    '''
    id: Mapped[int] = mapped_column(
        Integer,primary_key=True,autoincrement=True,sort_order=-1,comment="主键ID"
    )

    create_time: Mapped[datetime] = mapped_column(
        DateTime,nullable=False,default=datetime.now,comment="创建时间"
    )