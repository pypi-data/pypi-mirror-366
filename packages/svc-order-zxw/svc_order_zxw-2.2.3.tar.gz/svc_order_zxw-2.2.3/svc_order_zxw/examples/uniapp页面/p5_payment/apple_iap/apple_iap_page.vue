<template>
  <view class="container">
    <view class="header">
      <text class="title">苹果内购</text>
    </view>
    
    <view class="content">
      <view class="info-section">
        <text class="label">商品ID:</text>
        <input v-model="appleProductId" class="input" placeholder="请输入苹果商品ID" />
      </view>
      
      <view class="info-section">
        <text class="label">支付金额:</text>
        <input v-model.number="paymentPrice" class="input" type="digit" placeholder="请输入金额" />
      </view>
      
      <view class="info-section">
        <text class="label">用户ID:</text>
        <input v-model="userId" class="input" placeholder="请输入用户ID" />
      </view>
      
      <view class="button-section">
        <button class="pay-button" @click="handlePurchase">发起购买</button>
        <button class="restore-button" @click="handleRestore">恢复购买</button>
      </view>
      
      <view v-if="orderInfo" class="result-section">
        <text class="result-title">订单信息:</text>
        <view class="result-item">
          <text>订单号: {{ orderInfo.order_number }}</text>
        </view>
        <view class="result-item">
          <text>支付状态: {{ orderInfo.payment_status }}</text>
        </view>
        <view class="result-item">
          <text>商品名称: {{ orderInfo.product_name }}</text>
        </view>
        <view class="result-item">
          <text>应用名称: {{ orderInfo.app_name }}</text>
        </view>
        <view v-if="orderInfo.subscription_expire_date" class="result-item">
          <text>过期时间: {{ orderInfo.subscription_expire_date }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from "@dcloudio/uni-app";
import { appleIapApi } from './api_apple_iap.ts';

const appleProductId = ref('vip001');
const paymentPrice = ref(28.0);
const userId = ref('');
const quantity = ref(1);
const orderInfo = ref(null);

onLoad((options) => {
  if (options.userId) {
    userId.value = options.userId;
  }
  if (options.appleProductId) {
    appleProductId.value = options.appleProductId;
  }
  if (options.paymentPrice) {
    paymentPrice.value = parseFloat(options.paymentPrice);
  }
});

// 发起苹果内购
const handlePurchase = async () => {
  if (!userId.value || !appleProductId.value || !paymentPrice.value) {
    uni.showToast({
      title: '请填写完整信息',
      icon: 'none'
    });
    return;
  }

  try {
    uni.showLoading({
      title: '正在调用苹果支付...',
      mask: true
    });

    // 调用苹果内购API (这里需要集成苹果官方IAP SDK)
    // 这是一个示例，实际项目中需要使用苹果官方API
    const applePayResult = await simulateApplePay();
    
    if (!applePayResult.success) {
      throw new Error('苹果支付失败');
    }

    // 调用后端API验证支付
    const result = await appleIapApi.createOrder({
      user_id: userId.value,
      apple_product_id: appleProductId.value,
      payment_price: paymentPrice.value,
      quantity: quantity.value,
      transactionIdentifier: applePayResult.transactionIdentifier,
      transactionReceipt: applePayResult.transactionReceipt
    });

    orderInfo.value = result;
    uni.showToast({
      title: '支付成功',
      icon: 'success'
    });

  } catch (error) {
    console.error('支付失败:', error);
    uni.showToast({
      title: error.message || '支付失败',
      icon: 'none'
    });
  } finally {
    uni.hideLoading();
  }
};

// 恢复购买
const handleRestore = async () => {
  if (!userId.value) {
    uni.showToast({
      title: '请输入用户ID',
      icon: 'none'
    });
    return;
  }

  try {
    uni.showLoading({
      title: '正在恢复购买...',
      mask: true
    });

    // 这里需要从苹果获取交易标识符，示例中使用模拟数据
    const transactionIdentifier = await getAppleTransactionIdentifier();
    
    const result = await appleIapApi.restorePurchase({
      user_id: userId.value,
      transactionIdentifier: transactionIdentifier
    });

    orderInfo.value = result;
    uni.showToast({
      title: '恢复成功',
      icon: 'success'
    });

  } catch (error) {
    console.error('恢复购买失败:', error);
    uni.showToast({
      title: error.message || '恢复购买失败',
      icon: 'none'
    });
  } finally {
    uni.hideLoading();
  }
};

// 模拟苹果支付 (实际项目中需要集成苹果官方IAP SDK)
const simulateApplePay = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        success: true,
        transactionIdentifier: 'mock_transaction_' + Date.now(),
        transactionReceipt: 'mock_receipt_' + Date.now()
      });
    }, 2000);
  });
};

// 获取苹果交易标识符 (实际项目中需要从苹果API获取)
const getAppleTransactionIdentifier = async () => {
  // 这里应该调用苹果API获取用户的交易记录
  return 'mock_transaction_identifier';
};
</script>

<style scoped>
.container {
  padding: 20rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.content {
  padding: 0 20rpx;
}

.info-section {
  margin-bottom: 30rpx;
  background: white;
  padding: 20rpx;
  border-radius: 12rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.input {
  width: 100%;
  height: 80rpx;
  border: 1px solid #ddd;
  border-radius: 8rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
}

.button-section {
  margin: 40rpx 0;
}

.pay-button, .restore-button {
  width: 100%;
  height: 88rpx;
  border-radius: 12rpx;
  border: none;
  font-size: 32rpx;
  margin-bottom: 20rpx;
}

.pay-button {
  background: linear-gradient(45deg, #007AFF, #5AC8FA);
  color: white;
}

.restore-button {
  background: #FF9500;
  color: white;
}

.result-section {
  background: white;
  padding: 30rpx;
  border-radius: 12rpx;
  margin-top: 40rpx;
}

.result-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.result-item {
  margin-bottom: 15rpx;
  font-size: 28rpx;
  color: #666;
}
</style>