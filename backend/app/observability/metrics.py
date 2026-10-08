from fastapi import Request
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

REGISTRY = CollectorRegistry()

HTTP_REQUESTS_TOTAL = Counter(
    "workforce_http_requests_total",
    "Total number of HTTP requests.",
    ["method", "route", "status"],
    registry=REGISTRY,
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "workforce_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
    registry=REGISTRY,
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "workforce_http_requests_in_progress",
    "Number of HTTP requests currently being processed.",
    ["method", "route"],
    registry=REGISTRY,
)

from starlette.routing import Match

def get_route_template(request: Request) -> str:
    """
    Returns the route template (e.g. '/api/v1/projects/{project_id}') if a route is matched,
    otherwise returns '<unmatched>'.
    """
    route = request.scope.get("route")
    if not route:
        for r in request.app.routes:
            match, _ = r.matches(request.scope)
            if match == Match.FULL:
                route = r
                request.scope["route"] = r
                break
                
    if route and hasattr(route, "path"):
        return route.path
    
    return "<unmatched>"

