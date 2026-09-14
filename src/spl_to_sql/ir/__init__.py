"""Intermediate representation modules for spl-to-sql.

Contains two IR stages:
- spl_ir: SPL-shaped IR that mirrors SPL semantics (piped commands, eval).
- relational_ir: SQL-shaped IR that mirrors relational algebra (SELECT, JOIN).

And an optional transforms sub-module for IR-to-IR optimization passes.
"""
