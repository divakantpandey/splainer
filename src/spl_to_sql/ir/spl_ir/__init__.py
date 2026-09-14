"""SPL-shaped intermediate representation.

Mirrors SPL's own semantics: piped commands, eval expressions, field
references, etc. This is the direct output of the parser stage and
the input to the lowering step that produces the relational IR.
"""
