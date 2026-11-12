
'''
model包的含义：一般存放ORM映射表->类后的类
ORM模型：商品表-->类
'''
from decimal import Decimal

from sqlalchemy import String, Integer, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Products(Base):
    __tablename__ = 'products'
    __table_args__ = {"comment": "商品表"}

    category_id: Mapped[int] = mapped_column(
        Integer,ForeignKey("categories.id"),nullable=False,comment="商品种类"
    )

    name: Mapped[str] = mapped_column(
        String(50),nullable=False,comment="商品名称"
    )

    price: Mapped[Decimal] = mapped_column(
        DECIMAL(8,2),nullable=False,comment="商品价格"
    )

    stock: Mapped[int] = mapped_column(
        Integer,nullable=False,default=0,comment="商品库存"
    )

    shelf: Mapped[bool] = mapped_column(
        Boolean,nullable=False,default=True,comment="商品是否上架"
    )