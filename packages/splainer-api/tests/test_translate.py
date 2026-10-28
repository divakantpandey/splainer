def test_translate_route_mocked(mocker, client):
    mock_run = mocker.patch("splainer_sdk.client.run_pipeline")
    mock_result = mocker.Mock()
    mock_result.sql = "SELECT * FROM main"
    mock_result.error = None
    mock_result.used_llm = False
    mock_result.codegen_route = "deterministic"
    mock_result.execution_result = None
    mock_result.agent_logs = []
    mock_run.return_value = mock_result

    response = client.post("/v1/translate", json={"spl_query": "search index=main", "dialect": "postgres"})
    assert response.status_code == 200
    data = response.json()
    assert data["sql"] == "SELECT * FROM main"
    assert data["success"] is True

