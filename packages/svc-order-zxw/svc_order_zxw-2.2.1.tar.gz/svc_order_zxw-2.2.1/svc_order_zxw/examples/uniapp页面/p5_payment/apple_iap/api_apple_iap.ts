import {request} from '@/utils/request';
import { baseUrl } from '@/baseUrl'

// 定义API根地址
const BASE_URL = baseUrl;

// 定义请求类型
interface CreateAppleOrderRequest {
  user_id: string;
  apple_product_id: string;
  payment_price: number;
  quantity?: number;
  transactionIdentifier: string;
  transactionReceipt: string;
}

interface RestorePurchaseRequest {
  user_id: string;
  transactionIdentifier: string;
}

// 定义响应类型
interface ApplePaymentResponse {
  order_number: string;
  payment_status: string;
  payment_price: number;
  quantity: number;
  order_id: number;
  product_name: string;
  app_name: string;
  transaction_id?: string;
  original_transaction_id?: string;
  subscription_expire_date?: string;
  payment_method?: string;
}

// API函数
export const appleIapApi = {
  /**
   * 创建苹果内购订单
   * @param data 订单创建参数
   * @returns Promise<ApplePaymentResponse>
   */
  createOrder(data: CreateAppleOrderRequest): Promise<ApplePaymentResponse> {
    console.log(`${BASE_URL}/apple_pay/create_order`);
    return request({
      url: `${BASE_URL}/apple_pay/create_order`,
      method: 'POST',
      data
    }) as Promise<ApplePaymentResponse>;
  },

  /**
   * 恢复苹果内购
   * @param data 恢复购买参数
   * @returns Promise<ApplePaymentResponse>
   */
  restorePurchase(data: RestorePurchaseRequest): Promise<ApplePaymentResponse> {
    console.log(`${BASE_URL}/apple_pay/restore_purchase`);
    return request({
      url: `${BASE_URL}/apple_pay/restore_purchase`,
      method: 'POST',
      data
    }) as Promise<ApplePaymentResponse>;
  }
};