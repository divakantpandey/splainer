"""Tests for spl_to_sql.ir.relational_ir.nodes."""

from __future__ import annotations

from spl_to_sql.ir.relational_ir.nodes import (
    AggregateFunction,
    ColumnRef,
    FilterPredicate,
    JoinNode,
    JoinType,
    RelationalNode,
    RelationalQuery,
    SelectNode,
    SortDirection,
)


class TestRelationalNode:
    """Tests for RelationalNode base model."""

    def test_default_alias(self) -> None:
        """RelationalNode has None alias by default."""
        node = RelationalNode()
        assert node.alias is None


class TestColumnRef:
    """Tests for ColumnRef model."""

    def test_creation(self) -> None:
        """ColumnRef can be created with column name."""
        ref = ColumnRef(column="host")
        assert ref.column == "host"
        assert ref.table is None

    def test_with_table(self) -> None:
        """ColumnRef can include a table reference."""
        ref = ColumnRef(table="events", column="host")
        assert ref.table == "events"


class TestFilterPredicate:
    """Tests for FilterPredicate model."""

    def test_creation(self) -> None:
        """FilterPredicate stores expression text."""
        pred = FilterPredicate(expression_text="status = 500")
        assert pred.expression_text == "status = 500"


class TestAggregateFunction:
    """Tests for AggregateFunction model."""

    def test_creation(self) -> None:
        """AggregateFunction stores function name and args."""
        agg = AggregateFunction(function_name="COUNT", arguments=["*"])
        assert agg.function_name == "COUNT"
        assert agg.arguments == ["*"]


class TestSelectNode:
    """Tests for SelectNode model."""

    def test_minimal(self) -> None:
        """SelectNode can be created with minimal fields."""
        node = SelectNode(columns=["*"], from_table="events")
        assert node.columns == ["*"]
        assert node.from_table == "events"
        assert node.where is None
        assert node.group_by == []
        assert node.limit is None


class TestJoinNode:
    """Tests for JoinNode model."""

    def test_creation(self) -> None:
        """JoinNode stores join details."""
        node = JoinNode(
            join_type=JoinType.INNER,
            left_table="a",
            right_table="b",
            on_condition="a.id = b.id",
        )
        assert node.join_type == JoinType.INNER


class TestRelationalQuery:
    """Tests for RelationalQuery model."""

    def test_creation(self) -> None:
        """RelationalQuery wraps a SelectNode."""
        select = SelectNode(columns=["*"], from_table="events")
        query = RelationalQuery(select=select)
        assert query.select.from_table == "events"


class TestEnums:
    """Tests for enum values."""

    def test_join_types(self) -> None:
        """JoinType has expected values."""
        assert JoinType.INNER == "INNER"
        assert JoinType.LEFT == "LEFT"

    def test_sort_directions(self) -> None:
        """SortDirection has expected values."""
        assert SortDirection.ASC == "ASC"
        assert SortDirection.DESC == "DESC"
