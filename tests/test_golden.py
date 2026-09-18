import os
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

# TODO: Import the actual translate function once implemented
# from spl_to_sql.pipeline import translate

FIXTURES_DIR = Path(__file__).parent / "fixtures"
EXPECTED_DIR = FIXTURES_DIR / "expected"

def get_spl_files():
    if not FIXTURES_DIR.exists():
        return []
    return [f.name for f in FIXTURES_DIR.glob("*.spl")]

@pytest.mark.parametrize("spl_filename", get_spl_files())
def test_golden_queries(spl_filename: str):
    spl_path = FIXTURES_DIR / spl_filename
    expected_path = EXPECTED_DIR / f"{spl_filename.replace('.spl', '.sql')}"
    
    spl_query = spl_path.read_text().strip()
    
    # Skip if translate is not implemented yet
    pytest.skip("Pipeline not fully implemented yet")
    
    # result = translate(spl_query, dialect="postgres", config=...)
    # assert result.sql.strip() == expected_sql.strip()

