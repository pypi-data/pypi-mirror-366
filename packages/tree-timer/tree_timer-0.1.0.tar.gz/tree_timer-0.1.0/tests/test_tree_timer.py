"""Unit tests for the TreeTimer class."""

import time

from tree_timer import TreeTimer


def test_basic_timing() -> None:
    """Tests that basic timing works and total time is recorded."""
    with TreeTimer() as t:
        time.sleep(0.01)

    assert 0.009 <= t.total <= 0.1  # Allow some timing jitter


def test_add_scope() -> None:
    """Tests that a single child scope can be added and timed."""
    with TreeTimer() as t:
        with t.add_scope("load"):
            time.sleep(0.01)

    assert "load" in t._children
    assert isinstance(t._children["load"], TreeTimer)
    assert t._children["load"].total > 0


def test_add_series() -> None:
    """Tests that a series of child timers can be created and measured."""
    with TreeTimer() as t:
        series = t.add_series("steps", 3)
        for step in series:
            with step:
                time.sleep(0.005)

    assert "steps" in t._children
    assert isinstance(t._children["steps"], list)
    assert len(t._children["steps"]) == 3
    assert all(child.total > 0 for child in t._children["steps"])


def test_nested_scopes() -> None:
    """Tests nested scopes and total time aggregation."""
    with TreeTimer() as t:
        with t.add_scope("stage1") as s1:
            with s1.add_scope("step1"):
                time.sleep(0.005)
            with s1.add_scope("step2"):
                time.sleep(0.005)

    stage1 = t._children["stage1"]
    assert isinstance(stage1, TreeTimer)
    assert "step1" in stage1._children
    assert "step2" in stage1._children
    assert stage1.total > 0


def test_to_dict_output() -> None:
    """Tests that the to_dict method returns a valid structured dictionary."""
    with TreeTimer() as t:
        with t.add_scope("preprocess"):
            time.sleep(0.005)
        steps = t.add_series("epochs", 2)
        for s in steps:
            with s:
                time.sleep(0.002)

    d: dict = t.to_dict()
    assert isinstance(d, dict)
    assert d["name"] == "root"
    assert "children" in d
    assert any(child["name"] == "preprocess" for child in d["children"])
    assert any(child["name"] == "epochs" for child in d["children"])
    assert all("total" in child for child in d["children"])
