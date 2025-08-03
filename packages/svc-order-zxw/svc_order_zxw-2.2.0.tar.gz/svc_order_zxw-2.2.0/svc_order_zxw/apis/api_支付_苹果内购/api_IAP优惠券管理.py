"""
# File       : api_IAP优惠券管理.py
# Time       ：2025/7/29 15:24
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from app_tools_zxw.SDK_苹果应用服务.sdk_促销优惠管理 import 促销优惠签名结果, 苹果内购优惠管理服务
from svc_order_zxw.config import ApplePayConfig

Model促销优惠签名结果 = 促销优惠签名结果

# 创建苹果内购优惠管理服务实例
service = 苹果内购优惠管理服务(
        私钥文件路径=ApplePayConfig.私钥文件路径,
        密钥ID=ApplePayConfig.密钥ID,
        应用包ID=ApplePayConfig.应用包ID
    )


async def 生成IAP优惠卷(username: str, product_id: str, subscription_offer_id: str) -> Model促销优惠签名结果:
    """
    生成苹果内购优惠券签名

    Args:
        username: 用户名
        product_id: 产品ID，如 'vip001'
        subscription_offer_id: 订阅优惠ID，如 'vip001_discount_9'

    Returns:
        促销优惠签名结果: 包含签名和相关信息的结果对象
        {
          'product_id': 'vip001',
          'subscription_offer_id': 'vip001_discount_9',
          'application_username': 'user123',
          'nonce': UUID('13b49165-e087-4ae5-aa91-4ac1c08cdd8f'),
          'timestamp': 1753774116362,
          'signature': 'MEUCIQDpJbwIQ5sAIx2...',
          'created_at': '2025-07-29T15:28:36.365500'
        }
    """

    # 生成优惠券签名
    result = await service.生成促销优惠签名(
        product_id=product_id,
        subscription_offer_id=subscription_offer_id,
        application_username=username
    )

    return result
