
'''
model包的含义：一般存放ORM映射表->类后的类
ORM模型：商品分类表-->类.
'''
from decimal import Decimal

from sqlalchemy import String, Integer, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Categories(Base):
    '''
    __tablename__ ：由数据库中哪张表转换
    __table_args__：原本表的注释
    '''
    __tablename__ = 'categories'
    __table_args__ = {"comment": "商品分类表"}

    name: Mapped[str] = mapped_column(
        String(50),nullable=False,unique=True,comment="商品类别名"
    )