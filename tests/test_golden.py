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
    expected_sql = expected_path.read_text().strip()
    
    from spl_to_sql.parser import parse
    from spl_to_sql.ir.spl_ir.builder import build_spl_ir
    from spl_to_sql.ir.relational_ir.lowering import lower_to_relational
    from spl_to_sql.codegen.deterministic import generate_sql
    
    tree = parse(spl_query)
    spl_ir = build_spl_ir(tree)
    relational_ir = lower_to_relational(spl_ir)
    sql = generate_sql(relational_ir)
    
    assert sql.strip() == expected_sql

