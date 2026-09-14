"""SPL parser module — Stage 1 of the spl-to-sql pipeline.

Uses ANTLR4 to parse SPL query strings into parse trees. The grammar
definition lives in grammar/SPL.g4, and generated lexer/parser code
is placed in generated/ (gitignored, regenerated at build time).

TODO: Add ANTLR4 grammar generation to the build process.
"""
