"""
# File       : task1_定时更新商品.py
# Time       ：2025/6/26 15:04
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：启动时必须首先执行一次
定时更新apple商品信息
"""
from sqlalchemy.ext.asyncio import AsyncSession

from svc_order_zxw.db.get_db import get_db as get_db_order
from svc_order_zxw.db.crud1_applications import (
    get_application,
    create_application, PYD_ApplicationCreate,
)
from svc_order_zxw.db.crud2_products import (
    create_product, update_product, delete_product, PYD_ProductCreate, PYD_ProductUpdate,
    PYD_ProductResponse, get_product, ProductType)
from svc_order_zxw.config import ApplePayConfig

from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


class TASK1_更新苹果内购商品表:
    interval_minutes = 2  # 执行周期(分钟)
    get_db = get_db_order

    @staticmethod
    async def run(db: AsyncSession):
        logger.info("[svc_order_zxw task1]定时任务已启动")

        # 按app_name分组配置文件中的产品
        config_products_by_app = {}
        for apple_product_id, product_info in ApplePayConfig.products.items():
            app_name = product_info["app_name"]
            if app_name not in config_products_by_app:
                config_products_by_app[app_name] = []

            for product_name in product_info["product_names"]:
                config_products_by_app[app_name].append({
                    "product_name": product_name,
                    "apple_product_id": apple_product_id,
                    "product_info": product_info
                })

        # 对每个app进行处理
        for app_name, config_products in config_products_by_app.items():
            logger.info(f"[TASK1_更新商品表] 开始处理app: {app_name}")

            # 1. 获取或创建app
            app = await get_application(db, app_name, include_products=True)
            if app is None:
                new_app = PYD_ApplicationCreate(
                    name=app_name,
                )
                app = await create_application(db, new_app)
                logger.info(f"[TASK1_更新商品表] 创建新app: {app_name}")

            # 2. 获取数据库中的产品列表
            db_products: list[PYD_ProductResponse] = app.products

            # 3. 创建配置文件产品的组合键集合 (product_name, apple_product_id)
            config_keys = set()
            for config_product in config_products:
                config_keys.add((config_product["product_name"], config_product["apple_product_id"]))

            # 4. 创建数据库产品的组合键集合
            db_keys = set()
            db_product_map = {}  # (product_name, apple_product_id) -> PYD_ProductResponse
            for db_product in db_products:
                key = (db_product.name, db_product.apple_product_id)
                db_keys.add(key)
                db_product_map[key] = db_product

            # 5. 四类产品分类处理

            # 第1类：数据库中已存在的产品（需要更新）
            existing_keys = config_keys & db_keys
            logger.info(f"[TASK1_更新商品表] 第1类-需要更新的产品数量: {len(existing_keys)}")

            for product_name, apple_product_id in existing_keys:
                # 找到对应的配置信息
                config_product = next(cp for cp in config_products
                                    if cp["product_name"] == product_name and cp["apple_product_id"] == apple_product_id)

                db_product = db_product_map[(product_name, apple_product_id)]
                product_info = config_product["product_info"]

                # 检查是否需要更新
                needs_update = False
                update_data = {}

                if db_product.price != product_info["price"]:
                    update_data["price"] = product_info["price"]
                    needs_update = True

                if db_product.product_type != product_info["type"]:
                    update_data["product_type"] = product_info["type"]
                    needs_update = True

                expected_duration = f"{product_info.get('duration', -1)} {product_info.get('duration_type', 'day')}"
                if db_product.subscription_duration != expected_duration:
                    update_data["subscription_duration"] = expected_duration
                    needs_update = True

                if needs_update:
                    update_obj = PYD_ProductUpdate(**update_data)
                    await update_product(db, db_product.id, update_obj)
                    logger.info(f"[TASK1_更新商品表] 已更新产品: {product_name}, 更新字段: {list(update_data.keys())}")

            # 第2类：数据库中存在但配置文件中不存在的产品（需要删除）
            to_delete_keys = db_keys - config_keys
            logger.info(f"[TASK1_更新商品表] 第2类-需要删除的产品数量: {len(to_delete_keys)}")

            for product_name, apple_product_id in to_delete_keys:
                db_product = db_product_map[(product_name, apple_product_id)]
                await delete_product(db, db_product.id)
                logger.info(f"[TASK1_更新商品表] 已删除产品: {product_name}, apple_product_id: {apple_product_id}")

            # 第3类和第4类：配置文件中存在但数据库中不存在的产品（需要新增）
            to_create_keys = config_keys - db_keys
            logger.info(f"[TASK1_更新商品表] 第3/4类-需要新增的产品数量: {len(to_create_keys)}")

            for product_name, apple_product_id in to_create_keys:
                # 找到对应的配置信息
                config_product = next(cp for cp in config_products
                                    if cp["product_name"] == product_name and cp["apple_product_id"] == apple_product_id)

                product_info = config_product["product_info"]

                new_product = PYD_ProductCreate(
                    name=product_name,
                    app_id=app.id,
                    price=product_info["price"],
                    apple_product_id=apple_product_id,
                    product_type=product_info["type"],
                    subscription_duration=f"{product_info.get('duration', -1)} {product_info.get('duration_type', 'day')}"
                )

                created_product = await create_product(db, new_product)
                logger.info(f"[TASK1_更新商品表] 已创建产品: {product_name}, apple_product_id: {apple_product_id}")

        logger.info("[TASK1_更新商品表] 定时任务执行完成")
