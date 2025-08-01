import pytest
import os
from unittest.mock import patch, AsyncMock
from cadmium_fastapi.client import CadmiumClient, initialize_client, report_error

class TestCadmiumClient:
    def test_init_with_params(self):
        client = CadmiumClient(
            application_id="test-app",
            cd_secret="test-secret",
            cd_id="test-id"
        )
        assert client.application_id == "test-app"
        assert client.cd_secret == "test-secret"
        assert client.cd_id == "test-id"

    def test_init_with_env_vars(self):
        with patch.dict(os.environ, {
            'CADMIUM_APPLICATION_ID': 'env-app',
            'CADMIUM_CD_SECRET': 'env-secret',
            'CADMIUM_CD_ID': 'env-id'
        }):
            client = CadmiumClient()
            assert client.application_id == "env-app"
            assert client.cd_secret == "env-secret"
            assert client.cd_id == "env-id"

    def test_init_missing_config(self):
        with pytest.raises(ValueError, match="Missing required Cadmium configuration"):
            CadmiumClient()

    @pytest.mark.asyncio
    async def test_send_error_success(self):
        client = CadmiumClient(
            application_id="test-app",
            cd_secret="test-secret",
            cd_id="test-id"
        )
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            exception = ValueError("Test error")
            result = await client.send_error(exception)
            
            assert result is True

    @pytest.mark.asyncio
    async def test_send_error_failure(self):
        client = CadmiumClient(
            application_id="test-app",
            cd_secret="test-secret",
            cd_id="test-id"
        )
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("Network error")
            
            exception = ValueError("Test error")
            result = await client.send_error(exception)
            
            assert result is False