"""
KarmaCode - 健康检查 + 防休眠端点
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/ping")
async def ping():
    """防休眠 — 被外部 cron 定时调用"""
    return {
        "status": "awake",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "KarmaCode API is alive",
    }
