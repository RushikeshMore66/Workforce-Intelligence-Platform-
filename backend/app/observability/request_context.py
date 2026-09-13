from contextvars import ContextVar

request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default="-",
)


def get_request_id() -> str:
    return request_id_context.get()
