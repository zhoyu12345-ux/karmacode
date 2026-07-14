"""
KarmaCode - 支付 API
Stripe Checkout 集成: 创建会话、Webhook 处理、支付验证
"""

import os
import json
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# ============================================================
# Stripe 初始化
# ============================================================

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

# 产品定价 ID 映射 (Stripe Price ID ↔ 内部产品名)
PRICE_IDS = {
    "book_of_destiny": os.environ.get(
        "STRIPE_PRICE_BOOK_OF_DESTINY", "price_book_of_destiny"
    ),
}

# 产品定价金额（美分）
PRICE_AMOUNTS = {
    "book_of_destiny": 999,  # $9.99
}

BOOK_OF_DESTINY_PRICE = 999  # $9.99 in cents


# ============================================================
# 请求/响应模型
# ============================================================

class CreateCheckoutRequest(BaseModel):
    user_id: str
    price_id: str = "price_book_of_destiny"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    success: bool = True
    mock: bool = False
    checkout_url: str
    session_id: str
    message: str = ""


class VerifyResponse(BaseModel):
    status: str
    amount: float
    currency: str
    product_type: str = "book_of_destiny"
    created_at: str = ""
    mock: bool = False


class PaymentStatusResponse(BaseModel):
    valid: bool
    status: str
    message: str


# ============================================================
# POST /api/payment/create-checkout
# ============================================================

@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout(request: CreateCheckoutRequest):
    """
    创建 Stripe Checkout 会话

    - user_id: 用户 ID
    - price_id: 产品定价 ID（默认 "price_book_of_destiny"）
    - success_url: 支付成功后的回调 URL（可选）
    - cancel_url: 取消支付后的回调 URL（可选）
    """
    product_type = _resolve_product_type(request.price_id)

    # 开发阶段: Stripe 未配置时返回模拟链接
    if not STRIPE_SECRET_KEY:
        mock_session_id = f"mock_{request.user_id}_{product_type}"
        mock_url = (
            request.success_url or f"{FRONTEND_URL}/payment/success"
        ) + f"?session={mock_session_id}"

        _record_payment(
            user_id=request.user_id,
            stripe_session_id=mock_session_id,
            amount=PRICE_AMOUNTS.get(product_type, BOOK_OF_DESTINY_PRICE) / 100,
            product_type=product_type,
            status="mock_pending",
        )

        return CheckoutResponse(
            success=True,
            mock=True,
            checkout_url=mock_url,
            session_id=mock_session_id,
            message="Mock payment - Stripe not configured. In production, this redirects to Stripe Checkout.",
        )

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        success_url = (
            request.success_url
            or f"{FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        )
        cancel_url = request.cancel_url or f"{FRONTEND_URL}/payment/cancel"

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Book of Destiny (命之书)",
                            "description": (
                                "Your complete personalized BaZi analysis — "
                                "Love, Wealth, Life Chapters, and Annual Forecast. "
                                "One-time purchase with lifetime access and free annual updates."
                            ),
                            "images": ["https://karmacode.vercel.app/og-image.png"],
                        },
                        "unit_amount": PRICE_AMOUNTS.get(
                            product_type, BOOK_OF_DESTINY_PRICE
                        ),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": request.user_id,
                "product_type": product_type,
            },
        )

        # 在数据库中记录 pending 支付
        _record_payment(
            user_id=request.user_id,
            stripe_session_id=session.id,
            amount=PRICE_AMOUNTS.get(product_type, BOOK_OF_DESTINY_PRICE) / 100,
            product_type=product_type,
            status="pending",
        )

        return CheckoutResponse(
            success=True,
            mock=False,
            checkout_url=session.url or "",
            session_id=session.id,
            message="Redirecting to Stripe Checkout...",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Payment session creation failed: {str(e)}",
        )


# ============================================================
# POST /api/payment/webhook
# ============================================================

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    处理 Stripe Webhook 事件

    支持的事件:
    - checkout.session.completed: 支付完成
    - checkout.session.expired: 支付会话过期
    """
    if not STRIPE_SECRET_KEY:
        return {"received": True, "mock": True}

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        payload = await request.body()
        sig_header = request.headers.get("stripe-signature", "")

        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
        )

        # 处理 checkout.session.completed 事件
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            _handle_checkout_completed(session)

        # 处理 checkout.session.expired 事件
        elif event["type"] == "checkout.session.expired":
            session = event["data"]["object"]
            _handle_checkout_expired(session)

        return {"received": True, "event_type": event["type"]}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Webhook error: {str(e)}"
        )


def _handle_checkout_completed(session: dict):
    """处理支付完成事件"""
    stripe_session_id = session.get("id", "")
    metadata = session.get("metadata", {})
    user_id = metadata.get("user_id", "")
    product_type = metadata.get("product_type", "book_of_destiny")
    amount = (session.get("amount_total", 0) or 0) / 100

    _record_payment(
        user_id=user_id,
        stripe_session_id=stripe_session_id,
        amount=amount,
        product_type=product_type,
        status="completed",
    )

    print(
        f"[Payment] Completed: user={user_id} "
        f"amount=${amount:.2f} product={product_type}"
    )


def _handle_checkout_expired(session: dict):
    """处理支付会话过期事件"""
    stripe_session_id = session.get("id", "")
    metadata = session.get("metadata", {})
    user_id = metadata.get("user_id", "")
    product_type = metadata.get("product_type", "book_of_destiny")

    _record_payment(
        user_id=user_id,
        stripe_session_id=stripe_session_id,
        amount=0,
        product_type=product_type,
        status="expired",
    )

    print(f"[Payment] Expired: user={user_id} session={stripe_session_id}")


def _record_payment(
    user_id: str,
    stripe_session_id: str,
    amount: float,
    product_type: str,
    status: str,
):
    """
    将支付记录写入 Supabase 数据库
    使用 upsert (on_conflict=stripe_session_id) 避免重复记录
    """
    try:
        from supabase import create_client

        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

        if not supabase_url or not supabase_key:
            print(
                f"[Payment] Supabase not configured, "
                f"skipping DB record for {stripe_session_id}"
            )
            return

        client = create_client(supabase_url, supabase_key)

        client.table("payments").upsert(
            {
                "user_id": user_id,
                "stripe_session_id": stripe_session_id,
                "amount": amount,
                "currency": "usd",
                "status": status,
                "product_type": product_type,
            },
            on_conflict="stripe_session_id",
        ).execute()

        print(
            f"[Payment] Recorded: {stripe_session_id} -> {status} "
            f"(${amount:.2f})"
        )

    except Exception as e:
        print(f"[Payment] Failed to record payment: {e}")


# ============================================================
# GET /api/payment/verify/{session_id}
# ============================================================

@router.get("/verify/{session_id}", response_model=VerifyResponse)
async def verify_payment(session_id: str):
    """
    验证 Stripe Checkout 会话的支付状态

    - session_id: Stripe Checkout 会话 ID
    """
    # Mock 会话
    if session_id.startswith("mock_"):
        return VerifyResponse(
            status="mock_completed",
            amount=9.99,
            currency="usd",
            product_type="book_of_destiny",
            created_at="",
            mock=True,
        )

    if not STRIPE_SECRET_KEY:
        return VerifyResponse(
            status="pending",
            amount=0,
            currency="usd",
            product_type="book_of_destiny",
            created_at="",
            mock=True,
        )

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        session = stripe.checkout.Session.retrieve(session_id)

        payment_status = session.get("payment_status", "unpaid")
        amount = (session.get("amount_total", 0) or 0) / 100
        currency = session.get("currency", "usd")
        metadata = session.get("metadata", {})
        product_type = metadata.get("product_type", "book_of_destiny")
        created = session.get("created", 0)

        # 格式化创建时间
        from datetime import datetime, timezone

        created_str = datetime.fromtimestamp(
            created, tz=timezone.utc
        ).isoformat()

        return VerifyResponse(
            status=payment_status,
            amount=amount,
            currency=currency or "usd",
            product_type=product_type,
            created_at=created_str,
            mock=False,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}",
        )


# ============================================================
# GET /api/payment/status/{user_id}
# ============================================================

@router.get("/status/{user_id}", response_model=PaymentStatusResponse)
async def check_user_payment_status(
    user_id: str,
    product_type: str = "book_of_destiny",
):
    """
    检查用户是否已购买指定产品

    - user_id: 用户 ID
    - product_type: 产品类型（默认 "book_of_destiny"）
    """
    try:
        from supabase import create_client

        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

        if supabase_url and supabase_key:
            client = create_client(supabase_url, supabase_key)

            result = (
                client.table("payments")
                .select("status")
                .eq("user_id", user_id)
                .eq("product_type", product_type)
                .eq("status", "completed")
                .limit(1)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return PaymentStatusResponse(
                    valid=True,
                    status="completed",
                    message="You have purchased this product.",
                )

            return PaymentStatusResponse(
                valid=False,
                status="not_purchased",
                message="No valid purchase found for this product.",
            )

    except Exception as e:
        print(f"[Payment] Failed to check payment status: {e}")

    # 如果 Supabase 不可用，返回默认未购买状态
    return PaymentStatusResponse(
        valid=False,
        status="unavailable",
        message="Payment verification is currently unavailable.",
    )


# ============================================================
# GET /api/payment/config
# ============================================================

@router.get("/config")
async def get_stripe_config():
    """获取前端 Stripe 配置"""
    return {
        "publishable_key": os.environ.get("STRIPE_PUBLISHABLE_KEY", ""),
        "prices": {
            "book_of_destiny": {
                "amount": BOOK_OF_DESTINY_PRICE,
                "currency": "usd",
                "display": "$9.99",
            },
        },
        "mock": not bool(STRIPE_SECRET_KEY),
    }


# ============================================================
# 辅助函数
# ============================================================

def _resolve_product_type(price_id: str) -> str:
    """将 price_id 解析为内部产品类型"""
    # 反向映射: Stripe Price ID -> 产品名
    reverse_map = {v: k for k, v in PRICE_IDS.items()}
    if price_id in reverse_map:
        return reverse_map[price_id]
    if price_id in PRICE_IDS:
        return price_id
    return price_id
