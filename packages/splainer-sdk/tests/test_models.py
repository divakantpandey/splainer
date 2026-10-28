from splainer_sdk.models import Dialect, TranslateRequest

def test_dialect_enum():
    assert Dialect.POSTGRES == "postgres"
    assert Dialect.SNOWFLAKE == "snowflake"

def test_translate_request_defaults():
    req = TranslateRequest(spl_query="search")
    assert req.dialect == Dialect.POSTGRES
    assert req.execute is False

