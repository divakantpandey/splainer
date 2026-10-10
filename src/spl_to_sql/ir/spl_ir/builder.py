"""Parse tree → SPL IR builder.

Converts an ANTLR4 parse tree into the SPL-shaped intermediate
representation.
"""

from __future__ import annotations

import logging
from typing import Any

from spl_to_sql.parser.generated.SPLVisitor import SPLVisitor
from spl_to_sql.ir.spl_ir.nodes import (
    SPLPipeline,
    PipelineStage,
    SearchCommand,
    StatsCommand,
    Expression,
    BinaryOp,
    UnaryOp,
    FieldRef,
    Literal,
    WildcardExpr,
    InExpr,
    AggregationFunc,
)

logger = logging.getLogger(__name__)

class SPLIRBuildingVisitor(SPLVisitor):
    def visitQuery(self, ctx) -> SPLPipeline:
        stages = []
        if ctx.searchCommand():
            search_cmd = self.visit(ctx.searchCommand())
            stages.append(PipelineStage(command_name="search", command=search_cmd))
            
        for cmd_ctx in ctx.command():
            cmd = self.visit(cmd_ctx)
            if cmd is not None:
                # Get the name from the type
                type_name = type(cmd).__name__
                if type_name.endswith("Command"):
                    name = type_name[:-7].lower()
                else:
                    name = "unknown"
                stages.append(PipelineStage(command_name=name, command=cmd))
                
        return SPLPipeline(stages=stages)

    def visitSearchCommand(self, ctx) -> SearchCommand:
        expr_ctx = ctx.searchExpr()
        if not expr_ctx:
            return SearchCommand(expression=None)
            
        expr = self.visit(expr_ctx)
        
        # We can extract index and sourcetype if they exist as top level ANDs
        # For simplicity in this MVP iteration we just store the full expression tree
        # The relational lowering will parse it.
        return SearchCommand(
            expression=expr,
            source_text=ctx.getText()
        )

    def visitSearchExpr(self, ctx):
        if ctx.booleanExpr():
            return self.visit(ctx.booleanExpr())
        return None

    def visitBooleanExpr(self, ctx):
        # booleanExpr (AND | OR)? booleanExpr
        # NOT booleanExpr
        # comparisonExpr
        # '(' booleanExpr ')'
        
        if ctx.NOT():
            expr = self.visit(ctx.booleanExpr(0))
            return UnaryOp(op="NOT", expr=expr)
            
        if ctx.comparisonExpr():
            return self.visit(ctx.comparisonExpr())
            
        if len(ctx.booleanExpr()) == 2:
            left = self.visit(ctx.booleanExpr(0))
            right = self.visit(ctx.booleanExpr(1))
            op = "AND"
            if ctx.OR():
                op = "OR"
            elif ctx.AND():
                op = "AND"
            # implicit AND
            return BinaryOp(left=left, op=op, right=right)
            
        if len(ctx.booleanExpr()) == 1:
            # '(' booleanExpr ')'
            return self.visit(ctx.booleanExpr(0))
            
        return None

    def visitComparisonExpr(self, ctx):
        # IDENTIFIER compOp value
        # IDENTIFIER IN '(' valueList ')'
        # value  // bare keyword search
        
        if ctx.compOp():
            field = FieldRef(field_name=ctx.identifier().getText())
            op = ctx.compOp().getText()
            val = self.visit(ctx.value())
            return BinaryOp(left=field, op=op, right=val)
            
        if ctx.IN():
            field = FieldRef(field_name=ctx.identifier().getText())
            values = self.visit(ctx.valueList())
            return InExpr(field=field, values=values)
            
        if ctx.value():
            val = self.visit(ctx.value())
            # Bare keyword search maps to implicit _raw LIKE '*val*' or similar
            # In SPL, 'error' implies _raw LIKE '%error%'
            # For now, just return it as a BinaryOp against _raw
            return BinaryOp(left=FieldRef(field_name="_raw"), op="=", right=val)
            
        return None
        
    def visitValue(self, ctx):
        text = ctx.getText()
        if ctx.STRING():
            # strip quotes
            return Literal(value=text.strip('"\''))
        if ctx.NUMBER():
            return Literal(value=float(text) if '.' in text else int(text))
        if ctx.BOOLEAN():
            return Literal(value=text.lower() == 'true')
        if ctx.NULL_LIT():
            return Literal(value=None)
        if text == '*':
            return WildcardExpr(pattern='*')
        # IDENTIFIER fallback
        return Literal(value=text)

    def visitLiteral(self, ctx):
        text = ctx.getText()
        if ctx.STRING():
            return Literal(value=text.strip('"\''))
        if ctx.NUMBER():
            return Literal(value=float(text) if '.' in text else int(text))
        if ctx.BOOLEAN():
            return Literal(value=text.lower() == 'true')
        if ctx.NULL_LIT():
            return Literal(value=None)
        return Literal(value=text)
        
    def visitValueList(self, ctx):
        return [self.visit(v) for v in ctx.value()]

    def visitCommand(self, ctx):
        if ctx.statsCommand(): return self.visit(ctx.statsCommand())
        if ctx.evalCommand(): return self.visit(ctx.evalCommand())
        if ctx.whereCommand(): return self.visit(ctx.whereCommand())
        if ctx.tableCommand(): return self.visit(ctx.tableCommand())
        if ctx.fieldsCommand(): return self.visit(ctx.fieldsCommand())
        if ctx.sortCommand(): return self.visit(ctx.sortCommand())
        if ctx.headCommand(): return self.visit(ctx.headCommand())
        if ctx.tailCommand(): return self.visit(ctx.tailCommand())
        if ctx.renameCommand(): return self.visit(ctx.renameCommand())
        if ctx.dedupCommand(): return self.visit(ctx.dedupCommand())
        if ctx.topCommand(): return self.visit(ctx.topCommand())
        if ctx.rareCommand(): return self.visit(ctx.rareCommand())
        if ctx.unknownCommand(): return self.visit(ctx.unknownCommand())
        return None

    def visitStatsCommand(self, ctx) -> StatsCommand:
        aggs = []
        for agg_ctx in ctx.statsAgg():
            func = None
            field = None
            alias = None
            
            if agg_ctx.COUNT() and not agg_ctx.aggFunction():
                func = "count"
            elif agg_ctx.aggFunction():
                func = agg_ctx.aggFunction().getText().lower()
                
            if agg_ctx.identifier():
                idents = agg_ctx.identifier()
                if len(idents) == 1 and not agg_ctx.AS():
                    field = FieldRef(field_name=idents[0].getText())
                elif len(idents) == 1 and agg_ctx.AS():
                    alias = idents[0].getText()
                elif len(idents) == 2:
                    field = FieldRef(field_name=idents[0].getText())
                    alias = idents[1].getText()
                    
            aggs.append(AggregationFunc(function_name=func, field=field, alias=alias))
            
        groups = []
        if ctx.fieldList():
            groups = [FieldRef(field_name=ident.getText()) for ident in ctx.fieldList().identifier()]
            
        return StatsCommand(aggregations=aggs, group_by=groups)

    def visitEvalCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import EvalCommand, EvalAssignment
        assignments = []
        for assign_ctx in ctx.evalAssignment():
            target = assign_ctx.identifier().getText()
            expr = self.visit(assign_ctx.expression())
            assignments.append(EvalAssignment(target_field=target, expression=expr))
        return EvalCommand(assignments=assignments)

    def visitWhereCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import WhereCommand
        expr = self.visit(ctx.booleanExpr())
        return WhereCommand(expression=expr)

    def visitTableCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import TableCommand
        fields = [ident.getText() for ident in ctx.fieldList().identifier()]
        return TableCommand(fields=fields)

    def visitFieldsCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import FieldsCommand
        fields = [ident.getText() for ident in ctx.fieldList().identifier()]
        keep = True
        if ctx.getText().startswith("fields-"):
            keep = False
        return FieldsCommand(fields=fields, keep=keep)

    def visitSortCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import SortCommand
        # Needs careful parsing of signs, for MVP let's just get the identifiers
        # The identifiers are available as ctx.identifier()
        # For a true implementation we'd need to match the signs with identifiers
        # Since it's an MVP, let's just grab the text
        # Better: iterate through children
        fields = []
        current_sign = ""
        for child in ctx.getChildren():
            text = child.getText()
            if text in ("+", "-"):
                current_sign = text
            elif text != "sort" and text != ",":
                fields.append(f"{current_sign}{text}")
                current_sign = ""
        return SortCommand(fields=fields)

    def visitHeadCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import HeadCommand
        return HeadCommand(count=int(ctx.NUMBER().getText()))

    def visitTailCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import TailCommand
        return TailCommand(count=int(ctx.NUMBER().getText()))

    def visitRenameCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import RenameCommand, RenameItem
        renames = []
        for item in ctx.renameItem():
            idents = item.identifier()
            renames.append(RenameItem(old_name=idents[0].getText(), new_name=idents[1].getText()))
        return RenameCommand(renames=renames)

    def visitDedupCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import DedupCommand
        fields = [ident.getText() for ident in ctx.fieldList().identifier()]
        return DedupCommand(fields=fields)

    def visitTopCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import TopCommand
        limit = int(ctx.NUMBER().getText()) if ctx.NUMBER() else None
        field = ctx.identifier().getText()
        by = [ident.getText() for ident in ctx.fieldList().identifier()] if ctx.fieldList() else []
        return TopCommand(limit=limit, field=field, by=by)

    def visitRareCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import RareCommand
        limit = int(ctx.NUMBER().getText()) if ctx.NUMBER() else None
        field = ctx.identifier().getText()
        by = [ident.getText() for ident in ctx.fieldList().identifier()] if ctx.fieldList() else []
        return RareCommand(limit=limit, field=field, by=by)

    def visitUnknownCommand(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import UnknownCommand
        return UnknownCommand(command_name=ctx.identifier().getText(), raw_text=ctx.getText())

    def visitExpression(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import BinaryOp, FunctionCall, Literal, FieldRef
        if ctx.functionCall():
            return self.visit(ctx.functionCall())
        if ctx.literal():
            return self.visit(ctx.literal())
        if ctx.identifier():
            return FieldRef(field_name=ctx.identifier().getText())
        if len(ctx.expression()) == 1:
            return self.visit(ctx.expression(0))
        if len(ctx.expression()) == 2:
            left = self.visit(ctx.expression(0))
            right = self.visit(ctx.expression(1))
            op = ctx.getChild(1).getText()
            return BinaryOp(left=left, op=op, right=right)
        return None

    def visitFunctionCall(self, ctx):
        from spl_to_sql.ir.spl_ir.nodes import FunctionCall
        name = ctx.identifier().getText()
        args = []
        if ctx.exprList():
            args = [self.visit(e) for e in ctx.exprList().expression()]
        return FunctionCall(function_name=name, args=args)

def build_spl_ir(parse_tree: Any) -> SPLPipeline:
    visitor = SPLIRBuildingVisitor()
    return visitor.visit(parse_tree)
