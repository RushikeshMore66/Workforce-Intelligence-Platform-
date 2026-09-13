import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.observability.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
    get_route_template,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip if metrics are disabled or for the metrics endpoint itself
        if not settings.METRICS_ENABLED or request.url.path == settings.METRICS_PATH:
            return await call_next(request)

        method = request.method
        route_pending = "<pending>"

        start = time.perf_counter()

        HTTP_REQUESTS_IN_PROGRESS.labels(
            method=method,
            route=route_pending,
        ).inc()

        try:
            response = await call_next(request)

            route_final = get_route_template(request)

            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                route=route_final,
                status=str(response.status_code),
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                route=route_final,
            ).observe(time.perf_counter() - start)

            return response
        except Exception:
            route_final = get_route_template(request)
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                route=route_final,
                status="500",
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                route=route_final,
            ).observe(time.perf_counter() - start)
            raise
        finally:
            HTTP_REQUESTS_IN_PROGRESS.labels(
                method=method,
                route=route_pending,
            ).dec()
