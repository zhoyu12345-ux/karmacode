"""
KarmaCode - FastAPI 主程序
AI八字命理平台后端
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.bazi import router as bazi_router
from app.api.reading import router as reading_router
from app.api.payment import router as payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时
    print("KarmaCode API starting...")
    print(f"   Environment: {os.environ.get('ENV', 'development')}")
    yield
    # 关闭时
    print("KarmaCode API shutting down...")


app = FastAPI(
    title="KarmaCode API",
    description="AI-powered BaZi (八字) divination platform — bridging Eastern wisdom to the world",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS (允许Vercel前端访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://karmacode.vercel.app",
        os.environ.get("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(bazi_router, prefix="/api/bazi", tags=["BaZi"])
app.include_router(reading_router, prefix="/api/reading", tags=["Reading"])
app.include_router(payment_router, prefix="/api/payment", tags=["Payment"])


@app.get("/")
async def root():
    return {"message": "KarmaCode API", "version": "0.1.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ============================================================
# 全局异常处理
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
