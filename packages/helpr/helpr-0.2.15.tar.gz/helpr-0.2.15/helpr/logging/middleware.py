import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.logger import customLogger
from app.config import AppConfig

customLogger.debug("This is debug")
customLogger.info("Initializing FastAPI application...")
class LoggingContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        request_id = str(uuid.uuid4())

        user_id = getattr(request.state, "user_id", None)
        if user_id:
            customLogger.set_log_context(user_id=user_id)
        session_id=request.headers.get("X-CLY-SESSION-IDENTIFIER", "")
        if session_id:
            customLogger.set_log_context(session_id=session_id)
        customLogger.set_log_context(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            service="storehouse",
            env=AppConfig.ENV
        )

        try:
            response: Response = await call_next(request)
            return response
        finally:
            latency_ms = int((time.perf_counter() - start) * 1000)
            customLogger.set_log_context(latency_ms=latency_ms)
            customLogger.info(f"Latency in request: {latency_ms} ms", )
            customLogger.clear_log_context()