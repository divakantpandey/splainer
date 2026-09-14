// SPL.g4 — ANTLR4 grammar for Splunk SPL (Search Processing Language)
//
// This is a PLACEHOLDER grammar. It defines the minimal structure needed
// for the ANTLR4 toolchain to generate lexer/parser code. Real grammar
// rules will be added incrementally as SPL commands are supported.
//
// Usage:
//   antlr4 -Dlanguage=Python3 -visitor -o src/spl_to_sql/parser/generated SPL.g4
//
// TODO: Implement actual SPL grammar rules.

grammar SPL;

// --- Parser Rules ---

query
    : searchCommand (PIPE command)* EOF
    ;

searchCommand
    : SEARCH expression
    ;

command
    : IDENTIFIER expression*
    ;

expression
    : IDENTIFIER
    | STRING
    | NUMBER
    ;

// --- Lexer Rules ---

SEARCH : 'search' ;
PIPE   : '|' ;

IDENTIFIER : [a-zA-Z_] [a-zA-Z_0-9]* ;
STRING     : '"' (~["\\] | '\\' .)* '"' ;
NUMBER     : [0-9]+ ('.' [0-9]+)? ;

WS : [ \t\r\n]+ -> skip ;
