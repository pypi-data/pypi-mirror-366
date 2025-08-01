import pytest
from unittest.mock import patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from cadmium_fastapi import CadmiumMiddleware

@pytest.fixture
def app():
    app = FastAPI()
    
    app.add_middleware(
        CadmiumMiddleware,
        application_id="test-app",
        cd_secret="test-secret",
        cd_id="test-id"
    )
    
    @app.get("/")
    def read_root():
        return {"message": "Hello World"}
    
    @app.get("/error")
    def trigger_error():
        raise ValueError("Test error")
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_normal_request(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_error_handling(client):
    with patch('cadmium_fastapi.client.CadmiumClient.send_error') as mock_send:
        mock_send.return_value = True
        
        response = client.get("/error")
        assert response.status_code == 500  # FastAPI's default error response