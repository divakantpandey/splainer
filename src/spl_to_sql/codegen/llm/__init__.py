"""LLM-assisted SQL code generation.

Provides constrained-generation fallback for SQL constructs that
deterministic rules cannot handle. This module is ONLY invoked when
deterministic codegen fails — it is never the primary codegen path.

TODO: Implement LLM client integration.
TODO: Add monitoring/logging for LLM fallback usage.
"""
