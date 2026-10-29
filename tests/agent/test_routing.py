"""Tests for LangGraph agent routing logic."""

from __future__ import annotations

from spl_to_sql.agent.routing import (
    MAX_FIX_ATTEMPTS,
    route_after_codegen_det,
    route_after_codegen_llm,
    route_after_lowering,
    route_after_parse,
    route_after_parse_fix,
    route_after_validate,
    route_after_validate_fix,
)


def test_route_after_parse():
    # Success path
    state = {"parse_tree": "some_tree"}
    assert route_after_parse(state) == "ir_build"
    
    # Error path
    state = {"parse_tree": None}
    assert route_after_parse(state) == "parse_fix"


def test_route_after_parse_fix():
    # Retry path
    state = {"parse_fix_attempts": 0}
    assert route_after_parse_fix(state) == "parse"
    
    # Max attempts path
    state = {"parse_fix_attempts": MAX_FIX_ATTEMPTS}
    assert route_after_parse_fix(state) == "render_output"


def test_route_after_lowering():
    # Success path
    state = {"relational_ir": "some_ir"}
    assert route_after_lowering(state) == "codegen_deterministic"
    
    # Fallback path
    state = {"relational_ir": None}
    assert route_after_lowering(state) == "codegen_llm"


def test_route_after_codegen_det():
    # Success with execution
    state = {"generated_sql": "SELECT *", "execute": True}
    assert route_after_codegen_det(state) == "validate"
    
    # Success without execution
    state = {"generated_sql": "SELECT *", "execute": False}
    assert route_after_codegen_det(state) == "render_output"
    
    # Fallback path
    state = {"generated_sql": None}
    assert route_after_codegen_det(state) == "codegen_llm"


def test_route_after_validate():
    # Success path
    state = {"execution_result": "success"}
    assert route_after_validate(state) == "render_output"
    
    # Error path
    state = {"execution_result": None}
    assert route_after_validate(state) == "validate_fix"


def test_route_after_validate_fix():
    # Retry path
    state = {"validate_fix_attempts": 0}
    assert route_after_validate_fix(state) == "validate"
    
    # Max attempts path
    state = {"validate_fix_attempts": MAX_FIX_ATTEMPTS}
    assert route_after_validate_fix(state) == "render_output"


def test_route_after_codegen_llm():
    # Success with execution
    state = {"generated_sql": "SELECT *", "execute": True}
    assert route_after_codegen_llm(state) == "validate"
    
    # Success without execution
    state = {"generated_sql": "SELECT *", "execute": False}
    assert route_after_codegen_llm(state) == "render_output"
    
    # No SQL generated
    state = {"generated_sql": None, "execute": True}
    assert route_after_codegen_llm(state) == "render_output"
