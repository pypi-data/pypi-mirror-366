from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from svc_order_zxw.db.crud2_products import get_products
from svc_order_zxw.db import get_db

router = APIRouter(prefix="/products", tags=["商品查询_低权限"])


# 获取所有产品
async def i_get_products(
        app_name: str,
        is_apple_product: bool,
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)):
    return await get_products(db, app_name=app_name, is_apple_product=is_apple_product, skip=skip, limit=limit)


router.add_api_route("/get_all_products", i_get_products, methods=["GET"])
