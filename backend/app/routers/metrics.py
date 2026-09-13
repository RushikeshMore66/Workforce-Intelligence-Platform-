from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.observability.metrics import REGISTRY
from app.config import settings

router = APIRouter(tags=["observability"])

@router.get(settings.METRICS_PATH, include_in_schema=False)
def metrics():
    if not settings.METRICS_ENABLED:
        return Response(status_code=404)
        
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )
