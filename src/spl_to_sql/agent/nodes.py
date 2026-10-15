"""Nodes for the LangGraph pipeline.

These nodes form the steps of the SPL-to-SQL translation agent.
"""

from __future__ import annotations

import logging
from typing import Callable, Any

from spl_to_sql.agent.state import PipelineState
from spl_to_sql.agent.logging import start_log, start_timer, elapsed_ms, append_log
from spl_to_sql.parser import parse
from spl_to_sql.ir.spl_ir.builder import build_spl_ir
from spl_to_sql.ir.relational_ir.lowering import lower_to_relational
from spl_to_sql.codegen.deterministic import generate_sql
from spl_to_sql.codegen.llm.client import LLMClient
from spl_to_sql.codegen.llm.prompts import format_translation_prompt
from spl_to_sql.exceptions import ParseError, CodegenError, ExecutionError
from spl_to_sql.config import SplToSqlConfig
from spl_to_sql.execution.runner import SQLRunner
from spl_to_sql.agent.console_tree import render_agent_tree

logger = logging.getLogger(__name__)

def create_nodes(config: SplToSqlConfig) -> dict[str, Callable[[PipelineState], dict]]:
    llm_client = None
    if config.llm:
        llm_client = LLMClient(config=config.llm)

    sql_runner = None
    if config.database and config.database.connection_string and config.database.connection_string.get_secret_value():
        sql_runner = SQLRunner(config=config.database)

    def parse_node(state: PipelineState) -> dict:
        agent_logs = state.get("agent_logs", [])
        log = start_log("parse_node", "Parsing SPL query", "parse")
        start_t = start_timer()
        try:
            tree = parse(state["original_query"])
            log.finish("success", "Successfully parsed SPL query", elapsed_ms(start_t))
            return {"parse_tree": tree, "agent_logs": append_log(agent_logs, log)}
        except ParseError as e:
            log.finish("error", f"Parse error: {e}", elapsed_ms(start_t))
            attempts = state.get("parse_fix_attempts", 0)
            return {
                "current_error": str(e),
                "parse_fix_attempts": attempts,
                "agent_logs": append_log(agent_logs, log)
            }

    def parse_fix_node(state: PipelineState) -> dict:
        agent_logs = state.get("agent_logs", [])
        log = start_log("parse_fix_node", "Attempting to fix SPL query with LLM", "llm_fix")
        start_t = start_timer()
        attempts = state.get("parse_fix_attempts", 0) + 1
        
        try:
            if not llm_client:
                raise CodegenError("LLMClient not configured")
            prompt = (
                f"The following SPL query failed to parse:\n\n"
                f"{state['original_query']}\n\n"
                f"Error:\n{state.get('current_error', '')}\n\n"
                f"Please fix the syntax error and return ONLY the corrected SPL."
            )
            corrected_spl = llm_client.generate_sql(prompt)
            log.finish("success", "LLM corrected SPL query", elapsed_ms(start_t))
            return {
                "original_query": corrected_spl,
                "parse_fix_attempts": attempts,
                "agent_logs": append_log(agent_logs, log)
            }
        except Exception as e:
            log.finish("error", f"Failed to fix SPL query: {e}", elapsed_ms(start_t))
            return {
                "parse_fix_attempts": attempts,
                "agent_logs": append_log(agent_logs, log)
            }

    def ir_build_node(state: PipelineState) -> dict:
        agent_logs = state.get("agent_logs", [])
        log = start_log("ir_build_node", "Building SPL IR", "build_ir")
        start_t = start_timer()
        try:
            spl_ir = build_spl_ir(state["parse_tree"])
            stage_names = [s.command_name for s in spl_ir.stages] if hasattr(spl_ir, "stages") else []
            log.finish("success", f"Built SPL IR with {len(stage_names)} stages: {', '.join(stage_names)}", elapsed_ms(start_t))
            return {"spl_ir": spl_ir, "agent_logs": append_log(agent_logs, log)}
        except Exception as e:
            log.finish("error", f"IR build failed: {e}", elapsed_ms(start_t))
            return {"agent_logs": append_log(agent_logs, log)}

    def lowering_node(state: PipelineState) -> dict:
        agent_logs = state.get("agent_logs", [])
        log = start_log("lowering_node", "Lowering SPL IR to Relational IR", "lower_ir")
        start_t = start_timer()
        try:
            rel_ir = lower_to_relational(state["spl_ir"])
            log.finish("success", "Successfully lowered to Relational IR", elapsed_ms(start_t))
            return {"relational_ir": rel_ir, "agent_logs": append_log(agent_logs, log)}
        except CodegenError as e:
            log.finish("warning", f"Lowering unsupported: {e}", elapsed_ms(start_t))
            return {"relational_ir": None, "agent_logs": append_log(agent_logs, log)}
        except Exception as e:
            log.finish("error", f"Lowering failed: {e}", elapsed_ms(start_t))
            return {"relational_ir": None, "agent_logs": append_log(agent_logs, log)}

    def codegen_deterministic_node(state: PipelineState) -> dict:
        agent_logs = state.get("agent_logs", [])
        log = start_log("codegen_deterministic_node", "Generating SQL deterministically", "codegen")
        start_t = start_timer()
        try:
            sql = generate_sql(state["relational_ir"])
            log.finish("success", "Successfully generated SQL", elapsed_ms(start_t))
            return {
                "generated_sql": sql,
                "codegen_route": "deterministic",
                "used_llm": False,
                "agent_logs": append_log(agent_logs, log)
            }
        except CodegenError as e:
            log.finish("error", f"Deterministic codegen failed: {e}", elapsed_ms(start_t))
            return {"current_error": str(e), "agent_logs": append_log(agent_logs, log)}
        except Exception as e:
            log.finish("error", f"Deterministic codegen failed: {e}", elapsed_ms(start_t))
            return {"current_error": str(e), "agent_logs": append_log(agent_logs, log)}

    def codegen_llm_node(state: PipelineState) -> dict:
        agent_logs = state.get("agent_logs", [])
        log = start_log("codegen_llm_node", "Generating SQL with LLM", "codegen_llm")
        start_t = start_timer()
        try:
            if not llm_client:
                raise CodegenError("LLMClient not configured")
            # Build IR context for the prompt
            spl_ir = state.get("spl_ir")
            ir_json = ""
            if spl_ir and hasattr(spl_ir, "model_dump_json"):
                ir_json = spl_ir.model_dump_json(indent=2)
            prompt = format_translation_prompt(
                spl_description=state["original_query"],
                relational_ir_json=ir_json,
                dialect=state.get("dialect", "postgres"),
            )
            sql = llm_client.generate_sql(prompt)
            log.finish("success", "Successfully generated SQL with LLM", elapsed_ms(start_t))
            return {
                "generated_sql": sql,
                "codegen_route": "llm",
                "used_llm": True,
                "agent_logs": append_log(agent_logs, log)
            }
        except Exception as e:
            log.finish("error", f"LLM codegen failed: {e}", elapsed_ms(start_t))
            return {"current_error": str(e), "agent_logs": append_log(agent_logs, log)}

    def validate_node(state: PipelineState) -> dict:
        agent_logs = state.get("agent_logs", [])
        log = start_log("validate_node", "Executing SQL to validate", "execute")
        start_t = start_timer()
        attempts = state.get("validate_fix_attempts", 0)
        try:
            if not sql_runner:
                raise ExecutionError("SQLRunner not configured")
            sql_to_run = state.get("current_error_sql") or state.get("generated_sql", "")
            res = sql_runner.execute(sql_to_run)
            log.finish("success", "Query execution successful", elapsed_ms(start_t))
            return {"execution_result": res, "agent_logs": append_log(agent_logs, log)}
        except ExecutionError as e:
            log.finish("error", f"Execution failed: {e}", elapsed_ms(start_t))
            return {
                "current_error": str(e),
                "current_error_sql": state.get("generated_sql", ""),
                "validate_fix_attempts": attempts,
                "agent_logs": append_log(agent_logs, log)
            }
        except Exception as e:
            log.finish("error", f"Execution failed: {e}", elapsed_ms(start_t))
            return {
                "current_error": str(e),
                "current_error_sql": state.get("generated_sql", ""),
                "validate_fix_attempts": attempts,
                "agent_logs": append_log(agent_logs, log)
            }

    def validate_fix_node(state: PipelineState) -> dict:
        agent_logs = state.get("agent_logs", [])
        log = start_log("validate_fix_node", "Attempting to fix SQL with LLM", "llm_fix")
        start_t = start_timer()
        attempts = state.get("validate_fix_attempts", 0) + 1
        
        try:
            if not llm_client:
                raise CodegenError("LLMClient not configured")
            corrected_sql = llm_client.generate_corrected_sql(
                original_sql=state.get("current_error_sql", ""),
                error_message=state.get("current_error", ""),
                dialect=state.get("dialect", "snowflake")
            )
            log.finish("success", "LLM corrected SQL query", elapsed_ms(start_t))
            return {
                "generated_sql": corrected_sql,
                "current_error_sql": corrected_sql,
                "validate_fix_attempts": attempts,
                "agent_logs": append_log(agent_logs, log)
            }
        except Exception as e:
            log.finish("error", f"Failed to fix SQL: {e}", elapsed_ms(start_t))
            return {
                "validate_fix_attempts": attempts,
                "agent_logs": append_log(agent_logs, log)
            }

    def render_output_node(state: PipelineState) -> dict:
        """Render the agent tree and return empty updates."""
        if config.agent.console_tree_enabled:
            render_agent_tree(
                agent_logs=state.get("agent_logs", []),
                execution_result=state.get("execution_result"),
                generated_sql=state.get("generated_sql", ""),
            )
        return {}

    return {
        "parse_node": parse_node,
        "parse_fix_node": parse_fix_node,
        "ir_build_node": ir_build_node,
        "lowering_node": lowering_node,
        "codegen_deterministic_node": codegen_deterministic_node,
        "codegen_llm_node": codegen_llm_node,
        "validate_node": validate_node,
        "validate_fix_node": validate_fix_node,
        "render_output_node": render_output_node,
    }
