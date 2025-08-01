import os
import traceback
import logging
from typing import Optional, Dict, Any
import httpx
from fastapi import Request

logger = logging.getLogger(__name__)

CADMIUM_ENDPOINT = "https://cadmium.softwarescompound.in/logs"

class CadmiumClient:
    def __init__(
        self,
        application_id: Optional[str] = None,
        cd_secret: Optional[str] = None,
        cd_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        self.application_id = application_id or os.getenv("CADMIUM_APPLICATION_ID", "")
        self.cd_secret = cd_secret or os.getenv("CADMIUM_CD_SECRET", "")
        self.cd_id = cd_id or os.getenv("CADMIUM_CD_ID", "")
        self.endpoint = endpoint or CADMIUM_ENDPOINT
        
        if not all([self.application_id, self.cd_secret, self.cd_id]):
            raise ValueError(
                "Missing required Cadmium configuration. Please provide "
                "application_id, cd_secret, and cd_id either as parameters "
                "or environment variables (CADMIUM_APPLICATION_ID, "
                "CADMIUM_CD_SECRET, CADMIUM_CD_ID)"
            )

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Application-ID": self.application_id,
            "CD-Secret": self.cd_secret,
            "CD-ID": self.cd_id,
            "Content-Type": "application/json",
        }

    async def send_error(
        self,
        exception: Exception,
        request: Optional[Request] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send error to Cadmium server"""
        headers = self._get_headers()
        
        payload = {
            "error": str(exception),
            "traceback": traceback.format_exc(),
            "url": str(request.url) if request else "N/A",
            "method": request.method if request else "N/A",
        }
        
        if extra_data:
            payload.update(extra_data)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=5.0
                )
                response.raise_for_status()
                return True
        except httpx.RequestError as e:
            logger.error(f"Failed to send error to Cadmium server: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending to Cadmium: {e}")
            return False

# Global client instance
_client: Optional[CadmiumClient] = None

def initialize_client(
    application_id: Optional[str] = None,
    cd_secret: Optional[str] = None,
    cd_id: Optional[str] = None,
    endpoint: Optional[str] = None
) -> CadmiumClient:
    """Initialize the global Cadmium client"""
    global _client
    _client = CadmiumClient(application_id, cd_secret, cd_id, endpoint)
    return _client

def get_client() -> Optional[CadmiumClient]:
    """Get the global Cadmium client"""
    return _client

async def report_error(
    exception: Exception,
    request: Optional[Request] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> bool:
    """Report an error using the global client"""
    if not _client:
        logger.warning("Cadmium client not initialized. Call initialize_client() first.")
        return False
    
    return await _client.send_error(exception, request, extra_data)