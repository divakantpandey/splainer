"""Routing functions for the LangGraph pipeline.

These functions act as conditional edges between nodes, determining
the execution path based on the current state.
"""

from __future__ import annotations

from spl_to_sql.agent.state import PipelineState

MAX_FIX_ATTEMPTS = 3

def route_after_parse(state: PipelineState) -> str:
    if state.get("parse_tree") is not None:
        return "ir_build"
    return "parse_fix"

def route_after_parse_fix(state: PipelineState) -> str:
    if state.get("parse_fix_attempts", 0) >= MAX_FIX_ATTEMPTS:
        return "render_output"
    return "parse"

def route_after_lowering(state: PipelineState) -> str:
    if state.get("relational_ir") is not None:
        return "codegen_deterministic"
    return "codegen_llm"

def route_after_codegen_det(state: PipelineState) -> str:
    sql = state.get("generated_sql")
    if sql:
        if state.get("execute", False):
            return "validate"
        return "render_output"
    return "codegen_llm"

def route_after_validate(state: PipelineState) -> str:
    if state.get("execution_result") is not None:
        return "render_output"
    return "validate_fix"

def route_after_validate_fix(state: PipelineState) -> str:
    if state.get("validate_fix_attempts", 0) >= MAX_FIX_ATTEMPTS:
        return "render_output"
    return "validate"

def route_after_codegen_llm(state: PipelineState) -> str:
    sql = state.get("generated_sql")
    if sql and state.get("execute", False):
        return "validate"
    return "render_output"
