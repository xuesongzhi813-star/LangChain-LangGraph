from app.database import SessionLocal


#可以理解成，提交实例对象给Spring管理，这里就一定是操作一个数据库
def get_db():
    """为一次请求提供 Session，使用结束后关闭。"""
    with SessionLocal() as db:
        yield db