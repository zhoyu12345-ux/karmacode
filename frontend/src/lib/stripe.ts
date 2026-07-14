/**
 * KarmaCode - Stripe 支付集成 (前端)
 * Stripe Checkout 流程和支付验证
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================
// 类型定义
// ============================================================

export interface CheckoutSessionResponse {
  url: string;
  session_id: string;
}

export interface PaymentVerificationResponse {
  status: string;
  amount: number;
  currency: string;
  product_type: string;
  created_at: string;
}

export interface PaymentStatus {
  valid: boolean;
  status: string;
  message: string;
}

// ============================================================
// 创建 Stripe Checkout 会话
// ============================================================

/**
 * 创建 Stripe Checkout 会话并重定向用户到支付页面
 *
 * @param userId - 当前登录用户的 ID
 * @param priceId - Stripe Price ID（可选，默认使用后端配置）
 * @returns 重定向到 Stripe Checkout 页面
 */
export async function createCheckoutSession(
  userId: string,
  priceId: string = 'price_book_of_destiny'
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/api/payment/create-checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        price_id: priceId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create checkout session');
    }

    const data: CheckoutSessionResponse = await response.json();

    // 重定向到 Stripe Checkout
    if (data.url) {
      window.location.href = data.url;
    } else {
      throw new Error('No checkout URL returned');
    }
  } catch (error) {
    console.error('Create checkout session error:', error);
    throw error;
  }
}

// ============================================================
// 验证支付状态
// ============================================================

/**
 * 验证 Stripe Checkout 会话的支付状态
 *
 * @param sessionId - Stripe Checkout 会话 ID
 * @returns 支付验证结果
 */
export async function verifyPayment(
  sessionId: string
): Promise<PaymentVerificationResponse> {
  try {
    const response = await fetch(
      `${API_BASE}/api/payment/verify/${sessionId}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to verify payment');
    }

    return await response.json();
  } catch (error) {
    console.error('Verify payment error:', error);
    throw error;
  }
}

// ============================================================
// 检查用户付费状态
// ============================================================

/**
 * 检查用户是否已购买指定产品
 *
 * @param userId - 用户 ID
 * @param productType - 产品类型，默认 "book_of_destiny"
 * @returns 是否已付费
 */
export async function checkPaymentStatus(
  userId: string,
  productType: string = 'book_of_destiny'
): Promise<PaymentStatus> {
  try {
    const response = await fetch(
      `${API_BASE}/api/payment/status/${userId}?product_type=${productType}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to check payment status');
    }

    return await response.json();
  } catch (error) {
    console.error('Check payment status error:', error);
    return {
      valid: false,
      status: 'error',
      message: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

// ============================================================
// Stripe Checkout 回调处理
// ============================================================

/**
 * 处理 Stripe Checkout 成功回调
 * 从 URL 参数中提取 session_id 并验证支付
 *
 * 用法（在支付成功页面调用）:
 *   const result = await handleCheckoutReturn();
 *   if (result.success) { ... }
 */
export async function handleCheckoutReturn(): Promise<{
  success: boolean;
  status?: string;
  message: string;
}> {
  if (typeof window === 'undefined') {
    return { success: false, message: 'Not in browser' };
  }

  const params = new URLSearchParams(window.location.search);
  const sessionId = params.get('session_id');

  if (!sessionId) {
    return { success: false, message: 'No session ID found in URL' };
  }

  try {
    const result = await verifyPayment(sessionId);
    return {
      success: result.status === 'completed' || result.status === 'paid',
      status: result.status,
      message:
        result.status === 'completed' || result.status === 'paid'
          ? 'Payment verified successfully!'
          : `Payment status: ${result.status}`,
    };
  } catch (error) {
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Verification failed',
    };
  }
}
