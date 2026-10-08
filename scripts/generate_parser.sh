#!/usr/bin/env bash
set -e

# Generate ANTLR4 parser
# Needs antlr4 installed and in PATH, or antlr4-tools python package

echo "Generating ANTLR4 parser for SPL..."

mkdir -p src/spl_to_sql/parser/generated

antlr4 -Dlanguage=Python3 -visitor -listener \
  -o src/spl_to_sql/parser/generated \
  src/spl_to_sql/parser/grammar/SPL.g4

echo "Parser generation complete!"

