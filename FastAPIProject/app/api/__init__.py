from fastapi import APIRouter

from app.api.categories import category_router
from app.api.products import product_router

api_router = APIRouter(prefix="/api",tags=["可调用API汇总"])

#汇总所有可以调用的API
api_router.include_router(category_router)
api_router.include_router(product_router)
