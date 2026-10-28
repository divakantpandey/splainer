import pytest
from fastapi.testclient import TestClient
from splainer_api.app import create_app
from splainer_api.config import APISettings

@pytest.fixture
def api_settings():
    return APISettings(require_auth=False, rate_limit_enabled=False)

@pytest.fixture
def app(api_settings):
    return create_app(api_settings)

@pytest.fixture
def client(app):
    return TestClient(app)

