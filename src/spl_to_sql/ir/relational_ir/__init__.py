"""Relational-algebra-shaped intermediate representation.

Mirrors SQL semantics: SELECT, JOIN, WHERE, GROUP BY, ORDER BY, etc.
This is the output of the lowering step (spl_ir → relational_ir) and
the input to the codegen stage.
"""
