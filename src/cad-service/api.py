"""CAD API Routes"""

import os
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from .auth import verify_jwt, require_role, optional_auth, AuthenticatedUser
from .models import (
    BatchDetectRequest,
    BatchDetectResponse,
    AnomalyResult,
    FeedbackRequest,
    FeedbackResponse,
    ModelInfo,
    HealthResponse,
)
from .service import CADService

router = APIRouter()

RATE_LIMIT = os.getenv("RATE_LIMIT", "100/minute")


def get_cad_service() -> CADService:
    return CADService()


def rate_limit(request: Request):
    """Rate limit decorator helper"""
    from main import limiter

    return limiter.limit(RATE_LIMIT)(request)


@router.post("/detect/batch", response_model=BatchDetectResponse)
async def batch_detect(
    request: Request,
    batch_request: BatchDetectRequest,
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser, Depends(verify_jwt)],
) -> BatchDetectResponse:
    """批量检测接口"""
    try:
        from main import limiter

        limiter.limit(RATE_LIMIT)(request)
    except Exception:
        pass

    try:
        result = await service.batch_detect(
            data_date=batch_request.data_date,
            feature_version=batch_request.feature_version,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测服务异常: {str(e)}")


@router.get("/explain/{transaction_id}")
async def explain_transaction(
    request: Request,
    transaction_id: str,
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser | None, Depends(optional_auth)] = None,
):
    """获取异常解释"""
    try:
        from main import limiter

        limiter.limit(RATE_LIMIT)(request)
    except Exception:
        pass

    result = await service.get_explanation(transaction_id)
    if result is None:
        raise HTTPException(status_code=404, detail="交易不存在")
    return result


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: Request,
    feedback: FeedbackRequest,
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser, Depends(require_role("analyst", "supervisor"))],
) -> FeedbackResponse:
    """提交复核反馈"""
    try:
        from main import limiter

        limiter.limit(RATE_LIMIT)(request)
    except Exception:
        pass

    result = await service.submit_feedback(feedback)
    return result


@router.get("/models")
async def list_models(
    request: Request,
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser | None, Depends(optional_auth)] = None,
) -> list[ModelInfo]:
    """获取模型列表"""
    try:
        from main import limiter

        limiter.limit(RATE_LIMIT)(request)
    except Exception:
        pass

    return service.get_models()


@router.get("/health/degradation")
async def degradation_status(
    request: Request,
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser | None, Depends(optional_auth)] = None,
):
    """获取降级状态"""
    try:
        from main import limiter

        limiter.limit(RATE_LIMIT)(request)
    except Exception:
        pass

    return service.get_degradation_status()
