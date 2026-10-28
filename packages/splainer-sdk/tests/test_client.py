import pytest
from splainer_sdk import SplainerClient, Dialect

def test_health(sync_client):
    health = sync_client.health()
    assert health.status == "healthy"

def test_supported_dialects(sync_client):
    dialects = sync_client.supported_dialects
    assert "postgres" in dialects
    assert "snowflake" in dialects

def test_translate_simple_mocked(mocker, sync_client):
    mock_run = mocker.patch("splainer_sdk.client.run_pipeline")
    mock_result = mocker.Mock()
    mock_result.sql = "SELECT * FROM main"
    mock_result.error = None
    mock_result.used_llm = False
    mock_result.codegen_route = "deterministic"
    mock_result.execution_result = None
    mock_result.agent_logs = []
    mock_run.return_value = mock_result
    
    sql = sync_client.translate_simple("search index=main")
    assert sql == "SELECT * FROM main"

