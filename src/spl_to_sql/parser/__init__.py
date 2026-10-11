"""SPL parser module — Stage 1 of the spl-to-sql pipeline.

Uses ANTLR4 to parse SPL query strings into parse trees. The grammar
definition lives in grammar/SPL.g4, and generated lexer/parser code
is placed in generated/ (gitignored, regenerated at build time).

TODO: Add ANTLR4 grammar generation to the build process.
"""

from antlr4 import InputStream, CommonTokenStream

from spl_to_sql.parser.generated.SPLLexer import SPLLexer
from spl_to_sql.parser.generated.SPLParser import SPLParser
from spl_to_sql.parser.errors import SPLErrorCollector

def parse(query: str):
    """Parse an SPL query string into an ANTLR4 parse tree.

    Args:
        query: The SPL query string.

    Returns:
        The ANTLR4 parse tree root (query context).

    Raises:
        ParseError: If the query has syntax errors.
    """
    input_stream = InputStream(query)
    lexer = SPLLexer(input_stream)
    
    error_collector = SPLErrorCollector()
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_collector)

    token_stream = CommonTokenStream(lexer)
    parser = SPLParser(token_stream)
    
    parser.removeErrorListeners()
    parser.addErrorListener(error_collector)

    tree = parser.query()

    error_collector.raise_if_errors()

    return tree
