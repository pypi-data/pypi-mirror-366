import logging
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .client import CadmiumClient, initialize_client

logger = logging.getLogger(__name__)

class CadmiumMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        application_id: Optional[str] = None,
        cd_secret: Optional[str] = None,
        cd_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        capture_unhandled_exceptions: bool = True
    ):
        super().__init__(app)
        self.client = CadmiumClient(application_id, cd_secret, cd_id, endpoint)
        self.capture_unhandled_exceptions = capture_unhandled_exceptions
        
        # Initialize global client for manual error reporting
        initialize_client(application_id, cd_secret, cd_id, endpoint)
        
        logger.info("Cadmium FastAPI SDK initialized successfully")

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            if self.capture_unhandled_exceptions:
                await self.client.send_error(exc, request)
            
            # Re-raise the exception to maintain FastAPI's default error handling
            raise exc