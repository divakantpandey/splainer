import pytest
from splainer_sdk import SplainerClient

@pytest.fixture
def sync_client():
    return SplainerClient()

