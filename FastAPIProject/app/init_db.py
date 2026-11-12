from app.models.category import Categories
from app.models.product import Products
from app.database import Base, engine


#建表脚本
def main():
    """根据已经注册的模型，在数据库自动创建表"""
    print("开始执行创建表的脚本")
    Base.metadata.create_all(bind=engine)
    print("相关的表已经创建成功")

# 仅在主动运行此模块时建表，被其他模块导入时不执行。
if __name__ == "__main__":
    main()