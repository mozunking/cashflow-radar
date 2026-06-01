"""CAD FastAPI Service

资金异常检测API服务
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .api import router
from .models import (
    BatchDetectRequest,
    BatchDetectResponse,
    HealthResponse,
    ErrorResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("CAD Service starting...")
    yield
    # 关闭时清理
    print("CAD Service shutting down...")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="资金异常检测API",
    description="CAD - Capital Anomaly Detection Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 包含API路由
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> HealthResponse:
    """健康检查"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": f"CAD-{exc.status_code}",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
