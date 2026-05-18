"""CAD API Routes"""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
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


def get_cad_service() -> CADService:
    return CADService()


@router.post("/detect/batch", response_model=BatchDetectResponse)
async def batch_detect(
    request: BatchDetectRequest,
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser, Depends(verify_jwt)],
) -> BatchDetectResponse:
    """批量检测接口"""
    try:
        result = await service.batch_detect(
            data_date=request.data_date,
            feature_version=request.feature_version,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测服务异常: {str(e)}")


@router.get("/explain/{transaction_id}")
async def explain_transaction(
    transaction_id: str,
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser | None, Depends(optional_auth)] = None,
):
    """获取异常解释"""
    result = await service.get_explanation(transaction_id)
    if result is None:
        raise HTTPException(status_code=404, detail="交易不存在")
    return result


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser, Depends(require_role("analyst", "supervisor"))],
) -> FeedbackResponse:
    """提交复核反馈"""
    result = await service.submit_feedback(request)
    return result


@router.get("/models")
async def list_models(
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser | None, Depends(optional_auth)] = None,
) -> list[ModelInfo]:
    """获取模型列表"""
    return service.get_models()


@router.get("/health/degradation")
async def degradation_status(
    service: Annotated[CADService, Depends(get_cad_service)],
    user: Annotated[AuthenticatedUser | None, Depends(optional_auth)] = None,
):
    """获取降级状态"""
    return service.get_degradation_status()
