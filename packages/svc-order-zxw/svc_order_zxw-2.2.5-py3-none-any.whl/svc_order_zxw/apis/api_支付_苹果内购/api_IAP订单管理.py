"""
# File       : api_IAP订单管理.py
# Time       ：2025/7/28 14:34
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：需要前端登录的功能

print("1. 验证收据...")
        验证结果 = await 支付服务.验证收据_从应用收据(transactionReceipt2)
        print(f"验证结果: {验证结果.model_dump()}")
验证结果: {'商户订单号': '2000000973318333', '支付平台交易号': '2000000973318333', '原始交易号': '2000000971599396', '产品ID': 'vip001', '交易金额': 28.0, '交易状态': <OrderStatus.FINISHED: 'finished'>, '支付时间': '2025-07-31 09:44:27', '过期时间': '2025-07-31 09:49:27', '支付方式': <PaymentMethod.APPLE_PAY: 'apple_pay'>, '验证环境': 'Sandbox', '应用包ID': 'online.jingmu.fudaoyuan', '交易类型': 'Auto-Renewable Subscription', '交易原因': 'RENEWAL', '购买数量': 1, '货币代码': 'CNY', '原始价格': 28000, '店面代码': 'CHN', '应用交易ID': '704715577828757017', '是否试用期': None, '是否介绍性优惠期': None, '是否已退款': False, '退款时间': None, '退款原因': None, '备注': None}


订阅状态 = await 支付服务.获取订阅状态(transactionIdentifier2)
        print(f"订阅状态: ")
        print(f"环境: {订阅状态.环境}")
        print(f"最新收据: {订阅状态.最新收据}")
        print(f"最新交易信息: {订阅状态.最新交易信息}")
        print(f"待续费信息: {订阅状态.待续费信息}")
        print(f"是否有效订阅: {订阅状态.是否有效订阅}")
        print(f"订阅状态: {订阅状态.订阅状态}")
        print(f"过期时间: {订阅状态.过期时间}")
订阅状态:
环境: Sandbox
最新收据: None
最新交易信息: [SubscriptionTransactionInfo(transaction_id='2000000973318333', original_transaction_id='2000000971599396', product_id='vip001', bundle_id='online.jingmu.fudaoyuan', purchase_date='2025-07-31 09:44:27', purchase_date_ms='1753926267000', original_purchase_date='2025-07-29 11:44:06', original_purchase_date_ms='1753760646000', expires_date='2025-07-31 09:49:27', expires_date_ms='1753926567000', signed_date='2025-07-31 13:29:14', signed_date_ms='1753939754399', web_order_line_item_id='2000000107056054', subscription_group_identifier='21741812', quantity=1, type='Auto-Renewable Subscription', in_app_ownership_type='PURCHASED', transaction_reason='RENEWAL', environment='Sandbox', storefront='CHN', storefront_id='143465', price=28000, currency='CNY', app_transaction_id='704715577828757017', is_trial_period=None, is_in_intro_offer_period=None, is_upgraded=None, promotional_offer_id=None, offer_code_ref_name=None, cancellation_date=None, cancellation_date_ms=None, cancellation_reason=None, revocation_date=None, revocation_date_ms=None, revocation_reason=None)]
待续费信息: [PendingRenewalInfo(auto_renew_product_id='vip001', original_transaction_id='2000000971599396', product_id='vip001', auto_renew_status='0', is_in_billing_retry_period='False', price_consent_status=None, grace_period_expires_date=None, grace_period_expires_date_ms=None, promotional_offer_id=None, offer_code_ref_name=None, expiration_intent='1')]
是否有效订阅: False
订阅状态: expired
过期时间: 2025-07-31 09:49:27
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from pydantic import BaseModel, Field
from typing import Optional, Callable, Awaitable

from svc_order_zxw.db import get_db
from svc_order_zxw.db.crud2_products import get_product
from svc_order_zxw.db.crud3_orders import (
    create_order,
    get_order,
    PYD_OrderCreate,
)
from svc_order_zxw.db.crud4_payments import (
    create_payment,
    get_payment,
    update_payment,
    PYD_PaymentResponse,
    PYD_PaymentUpdate,
    PYD_PaymentCreate,
)
from svc_order_zxw.db.models import Payment, Product, Application, Order, ProductType
from svc_order_zxw.异常代码 import 订单_异常代码, 商品_异常代码, 支付_异常代码, 其他_异常代码
from svc_order_zxw.config import AliPayConfig
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod

from svc_order_zxw.apis.api_支付_苹果内购.func_生成订单号 import 生成订单号

from app_tools_zxw.SDK_苹果应用服务.sdk_支付验证 import 苹果内购支付服务_官方库, ApplePaymentResult, SubscriptionStatus
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

from svc_order_zxw.config import ApplePayConfig

logger = setup_logger(__name__)
router = APIRouter(prefix="/apple_pay", tags=["苹果内购"])

apple支付服务 = 苹果内购支付服务_官方库(**{
    "私钥文件路径": ApplePayConfig.私钥文件路径,
    "密钥ID": ApplePayConfig.密钥ID,
    "发行者ID": ApplePayConfig.发行者ID,
    "应用包ID": ApplePayConfig.应用包ID,
    "是否沙盒环境": ApplePayConfig.是否沙盒环境,
    "苹果ID": ApplePayConfig.苹果ID
})


class 请求_IPA_创建订单(BaseModel):
    user_id: str
    apple_product_id: str
    payment_price: float
    quantity: int = Field(default=1)
    transactionIdentifier: str
    transactionReceipt: str


class 返回_IPA_订单信息(BaseModel):
    user_id: str
    product_id: int
    order_number: str

    total_price: float  # 总金额
    payment_price: float  # 实际支付金额
    quantity: int
    status: str


class 返回_IPA_支付信息(BaseModel):
    order_number: str
    payment_status: str  # 理论上是OrderStatus类型, 在schemas_payments中
    payment_price: float
    quantity: int
    order_id: int
    product_name: str
    app_name: str


async def func0_查询或创建订单_仅限IAP(
        db: AsyncSession,
        user_id: str,
        apple_product_id: str,
        payment_price: float,
        quantity: int,
        transactionReceipt: str,
        transactionIdentifier: str,
        original_transaction_id: str,
        subscription_expire_date: datetime | None,
        payment_status: OrderStatus) -> tuple[PYD_PaymentResponse, Product]:
    # 0. 查询支付单是否存在
    # 因为Order和Payment是1对1关系，所以如果Payment不存在，则Order也不存在
    # 【此逻辑仅与本文件代码匹配，因为创建订单时，Order和Payment是同时创建的】
    query = select(Payment).options(joinedload(Payment.order)).where(
        Payment.apple_transaction_id == transactionIdentifier)
    result = await db.execute(query)
    existing_payment = result.scalar_one_or_none()
    if existing_payment:
        return existing_payment

    # 1.查询Product,得到product_id
    product = await select(Product).where(Product.apple_product_id == apple_product_id).options(
        joinedload(Product.app)).first()
    if not product:
        raise HTTPException_AppToolsSZXW(
            error_code=商品_异常代码.商品不存在.value,
            detail="商品不存在",
            http_status_code=404
        )

    # 1. 创建新order
    new_order = await create_order(db, PYD_OrderCreate(
        order_number=生成订单号(),
        user_id=user_id,
        total_price=payment_price,
        quantity=quantity,
        product_id=product.id,
        original_transaction_id=original_transaction_id,
        subscription_expire_date=subscription_expire_date
    ))

    # 2. 创建Payment
    new_payment: PYD_PaymentResponse = await create_payment(db, PYD_PaymentCreate(
        order_id=new_order.id,
        payment_price=payment_price,
        payment_method=PaymentMethod.APPLE_PAY,
        payment_status=payment_status,
        callback_url=None,
        payment_url=None,
        apple_transaction_id=transactionReceipt,
        apple_receipt=transactionReceipt
    ))

    return new_payment, product


async def step1_验证收据_创建订单(request: 请求_IPA_创建订单, db: AsyncSession = Depends(get_db)):
    # 1.验证收据
    验证结果 = await apple支付服务.验证收据_从应用收据(request.transactionReceipt)
    logger.info(f"苹果支付收据验证结果: {验证结果.model_dump()}")

    # 3. 创建订单
    new_payment, product = await func0_查询或创建订单_仅限IAP(
        db=db,
        user_id=request.user_id,
        apple_product_id=request.apple_product_id,
        payment_price=request.payment_price,
        quantity=request.quantity,
        transactionReceipt=request.transactionReceipt,
        transactionIdentifier=request.transactionIdentifier,
        original_transaction_id=验证结果.原始交易号,
        subscription_expire_date=datetime.strptime(验证结果.过期时间, "%Y-%m-%d %H:%M:%S"),
        payment_status=验证结果.交易状态
    )
    return 返回_IPA_支付信息(
        order_number=new_payment.order.order_number,
        payment_status=new_payment.payment_status.value,
        payment_price=new_payment.payment_price,
        quantity=new_payment.order.quantity,
        order_id=new_payment.order.id,
        product_name=product.name,
        app_name=product.app.name,
        transaction_id=new_payment.apple_transaction_id,
        original_transaction_id=new_payment.order.original_transaction_id,
        subscription_expire_date=new_payment.order.subscription_expire_date,
        payment_method=new_payment.payment_method,
    )


class 请求_IPA_恢复购买(BaseModel):
    user_id: str
    transactionIdentifier: str
    apple_product_id: str


async def step2_恢复购买(request: 请求_IPA_恢复购买, db: AsyncSession = Depends(get_db)):
    """
    Apple IAP 恢复购买
    1. 如果是订阅型商品，transactionIdentifier是原始交易号
    2. 如果是非订阅型商品，transactionIdentifier是应用收据
    """
    # 0. 根据apple_product_id查询ApplePayConfig中定义的商品类型
    product_type = ApplePayConfig.products[request.apple_product_id]["type"]

    if product_type in [ProductType.AUTO_RENEWABLE.value, ProductType.NON_RENEWABLE.value]:
        # 1. 验证订阅
        订阅状态: SubscriptionStatus = await apple支付服务.获取订阅状态(request.transactionIdentifier)
        logger.info(
            f"恢复购买 - 订阅状态: {订阅状态.订阅状态}, 有效订阅: {订阅状态.是否有效订阅}, 最新交易信息: {订阅状态.最新交易信息}")
        if not 订阅状态.最新交易信息:
            raise HTTPException_AppToolsSZXW(
                error_code=支付_异常代码.支付记录不存在.value,
                detail="未找到交易信息",
                http_status_code=404
            )
        最新交易 = 订阅状态.最新交易信息[0]
        # 2. 查询或创建订单
        my_payment, product = await func0_查询或创建订单_仅限IAP(
            db=db,
            user_id=request.user_id,
            apple_product_id=最新交易.product_id,
            payment_price=最新交易.price / 100,
            quantity=最新交易.quantity,
            transactionReceipt=request.transactionReceipt,
            transactionIdentifier=最新交易.transaction_id,
            original_transaction_id=最新交易.original_transaction_id,
            subscription_expire_date=datetime.strptime(最新交易.expires_date, "%Y-%m-%d %H:%M:%S"),
            payment_status=OrderStatus.FINISHED if 订阅状态.是否有效订阅 else OrderStatus.CANCELLED
        )

        # 3. 更新支付状态，并返回支付信息
        current_status = OrderStatus.FINISHED if 订阅状态.是否有效订阅 else OrderStatus.CANCELLED
        if my_payment.payment_status != current_status:
            await update_payment(db, my_payment.id, PYD_PaymentUpdate(
                payment_status=current_status
            ))
            logger.info(f"更新支付状态: {my_payment.id} -> {current_status}")

    else:
        # 1. 验证非订阅型商品
        最新交易 = await apple支付服务.验证特定交易(request.transactionIdentifier)
        logger.info(f"恢复购买 - 验证结果: {最新交易.model_dump()}")

        # 2. 查询或创建订单
        my_payment, product = await func0_查询或创建订单_仅限IAP(
            db=db,
            user_id=request.user_id,
            apple_product_id=最新交易.产品ID,
            payment_price=最新交易.交易金额,
            quantity=最新交易.购买数量,
            transactionReceipt=request.transactionIdentifier,
            transactionIdentifier=最新交易.支付平台交易号,
            original_transaction_id=最新交易.原始交易号,
            subscription_expire_date=None,
            payment_status=最新交易.交易状态
        )

        # 3. 更新支付状态，并返回支付信息
        current_status = 最新交易.交易状态
        if my_payment.payment_status != current_status:
            await update_payment(db, my_payment.id, PYD_PaymentUpdate(
                payment_status=current_status
            ))
            logger.info(f"更新支付状态: {my_payment.id} -> {current_status}")

    return 返回_IPA_支付信息(
        order_number=my_payment.order.order_number,
        payment_status=current_status.value,
        payment_price=my_payment.payment_price,
        quantity=my_payment.order.quantity,
        order_id=my_payment.order.id,
        product_name=product.name,
        app_name=product.app.name,
        transaction_id=my_payment.apple_transaction_id,
        original_transaction_id=my_payment.order.original_transaction_id,
        subscription_expire_date=my_payment.order.subscription_expire_date,
        payment_method=my_payment.payment_method
    )


router.add_api_route("/create_order", step1_验证收据_创建订单, methods=["POST"])
router.add_api_route("/restore_subscription", step2_恢复购买, methods=["POST"])
