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
    : SEARCH? searchExpr
    ;

command
    : statsCommand
    | evalCommand
    | whereCommand
    | tableCommand
    | fieldsCommand
    | sortCommand
    | headCommand
    | tailCommand
    | renameCommand
    | dedupCommand
    | topCommand
    | rareCommand
    | unknownCommand
    ;

statsCommand
    : STATS statsAgg (','? statsAgg)* (BY fieldList)?
    ;

statsAgg
    : aggFunction '(' identifier ')' (AS identifier)?
    | COUNT (AS identifier)?
    ;

aggFunction
    : COUNT | SUM | AVG | MIN | MAX | DC | VALUES
    ;

evalCommand
    : EVAL evalAssignment (',' evalAssignment)*
    ;

evalAssignment
    : identifier '=' expression
    ;

whereCommand
    : WHERE booleanExpr
    ;

tableCommand
    : TABLE fieldList
    ;

fieldsCommand
    : FIELDS ('+' | '-')? fieldList
    ;

sortCommand
    : SORT ( '+' | '-' )? identifier (','? ( '+' | '-' )? identifier)*
    ;

headCommand
    : HEAD NUMBER
    ;

tailCommand
    : TAIL NUMBER
    ;

renameCommand
    : RENAME renameItem (','? renameItem)*
    ;

renameItem
    : identifier AS identifier
    ;

dedupCommand
    : DEDUP fieldList
    ;

topCommand
    : TOP (NUMBER)? identifier (BY fieldList)?
    ;

rareCommand
    : RARE (NUMBER)? identifier (BY fieldList)?
    ;

unknownCommand
    : identifier argument*
    ;

argument
    : identifier
    | STRING
    | NUMBER
    | '='
    | '+'
    | '-'
    | '*'
    | '/'
    | '.'
    | '('
    | ')'
    ;

searchExpr
    : booleanExpr
    ;

booleanExpr
    : booleanExpr (AND | OR)? booleanExpr
    | NOT booleanExpr
    | comparisonExpr
    | '(' booleanExpr ')'
    ;

comparisonExpr
    : identifier compOp value
    | identifier IN '(' valueList ')'
    | value  // bare keyword search
    ;

compOp
    : '=' | '!=' | '<' | '>' | '<=' | '>=' | LIKE
    ;

value
    : STRING
    | NUMBER
    | identifier
    | BOOLEAN
    | NULL_LIT
    | '*' // wildcard
    ;

valueList
    : value (',' value)*
    ;

fieldList
    : identifier (','? identifier)*
    ;

expression
    : expression ('+' | '-' | '*' | '/' | '.') expression
    | functionCall
    | identifier
    | literal
    | '(' expression ')'
    ;

functionCall
    : identifier '(' exprList? ')'
    ;

exprList
    : expression (',' expression)*
    ;

literal
    : STRING
    | NUMBER
    | BOOLEAN
    | NULL_LIT
    ;

identifier
    : IDENTIFIER
    | COUNT
    | SUM
    | AVG
    | MIN
    | MAX
    | DC
    | VALUES
    | SEARCH
    | EVAL
    | WHERE
    | STATS
    | TABLE
    | FIELDS
    | SORT
    | HEAD
    | TAIL
    | RENAME
    | DEDUP
    | TOP
    | RARE
    | BY
    | AS
    | AND
    | OR
    | NOT
    | IN
    | LIKE
    ;

// --- Lexer Rules ---

// Case-insensitive keywords
SEARCH  : [sS][eE][aA][rR][cC][hH] ;
STATS   : [sS][tT][aA][tT][sS] ;
EVAL    : [eE][vV][aA][lL] ;
WHERE   : [wW][hH][eE][rR][eE] ;
TABLE   : [tT][aA][bB][lL][eE] ;
FIELDS  : [fF][iI][eE][lL][dD][sS] ;
SORT    : [sS][oO][rR][tT] ;
HEAD    : [hH][eE][aA][dD] ;
TAIL    : [tT][aA][iI][lL] ;
RENAME  : [rR][eE][nN][aA][mM][eE] ;
DEDUP   : [dD][eE][dD][uU][pP] ;
TOP     : [tT][oO][pP] ;
RARE    : [rR][aA][rR][eE] ;

BY      : [bB][yY] ;
AS      : [aA][sS] ;
AND     : [aA][nN][dD] ;
OR      : [oO][rR] ;
NOT     : [nN][oO][tT] ;
IN      : [iI][nN] ;
LIKE    : [lL][iI][kK][eE] ;

COUNT   : [cC][oO][uU][nN][tT] ;
SUM     : [sS][uU][mM] ;
AVG     : [aA][vV][gG] ;
MIN     : [mM][iI][nN] ;
MAX     : [mM][aA][xX] ;
DC      : [dD][cC] ;
VALUES  : [vV][aA][lL][uU][eE][sS] ;

BOOLEAN : [tT][rR][uU][eE] | [fF][aA][lL][sS][eE] ;
NULL_LIT: [nN][uU][lL][lL] ;

PIPE   : '|' ;

IDENTIFIER : [a-zA-Z_] [a-zA-Z_0-9.-]* ;
STRING     : '"' (~["\\] | '\\' .)* '"' ;
NUMBER     : [0-9]+ ('.' [0-9]+)? ;

WS : [ \t\r\n]+ -> skip ;
