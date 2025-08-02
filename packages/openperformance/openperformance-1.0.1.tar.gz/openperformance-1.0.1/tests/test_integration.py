import pytest
from fastapi.testclient import TestClient
from python.mlperf.api.main import app
from python.mlperf.api import main as api_main
from starlette.requests import Request

# Remove RateLimitMiddleware for testing
app.user_middleware = [
    m for m in app.user_middleware
    if m.cls.__name__ != "RateLimitMiddleware"
]
app.middleware_stack = app.build_middleware_stack()

def override_user_dependency(request: Request = None):
    class DummyUser:
        id = 1
        username = "testuser"
        is_active = True
        is_superuser = False
        role = "user"
    return DummyUser()

app.dependency_overrides[api_main.get_current_user] = override_user_dependency
app.dependency_overrides[api_main.require_user] = override_user_dependency

client = TestClient(app)


def test_full_workflow():
    # Test system metrics endpoint
    metrics_response = client.get("/system/metrics")
    assert metrics_response.status_code == 200
    metrics = metrics_response.json()
    assert "gpu_info" in metrics
    assert "memory_usage" in metrics
    
    # Test performance analysis
    analysis_request = {
        "framework": "pytorch",
        "batch_size": 32,
        "model_configuration": {
            "size_gb": 1.5,
            "layers": 24,
            "parameters": 175000000
        },
        "hardware_info": {
            "gpus": [gpu for gpu in metrics["gpu_info"]]
        }
    }
    analysis_response = client.post("/analyze/performance", json=analysis_request)
    assert analysis_response.status_code == 200
    recommendations = analysis_response.json()
    assert len(recommendations) > 0
    assert all(key in rec for rec in recommendations for key in ["area", "suggestion", "estimated_impact"])

def test_error_handling():
    # Test invalid framework
    invalid_request = {
        "framework": "invalid",
        "batch_size": 32,
        "model_configuration": {},
        "hardware_info": {}
    }
    response = client.post("/analyze/performance", json=invalid_request)
    assert response.status_code == 500
    
def test_api_health():
    """Test basic API health."""
    # For now, just test that the app can be imported and created
    assert app is not None
    assert hasattr(app, 'routes')
    assert len(app.routes) > 0 