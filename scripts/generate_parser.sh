#!/usr/bin/env bash
set -e

# Generate ANTLR4 parser
# Needs antlr4 installed and in PATH, or antlr4-tools python package

echo "Generating ANTLR4 parser for SPL..."

mkdir -p src/spl_to_sql/parser/generated
rm -rf src/spl_to_sql/parser/generated/*

cd src/spl_to_sql/parser/grammar
PATH="/opt/homebrew/opt/openjdk/bin:$PATH" ANTLR4_TOOLS_ANTLR_VERSION=4.13.1 ../../../../.venv/bin/antlr4 -Dlanguage=Python3 -visitor -listener -o ../generated SPL.g4
cd ../generated
touch __init__.py

echo "Parser generation complete!"
