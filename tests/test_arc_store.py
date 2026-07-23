"""Tests for Arc storage."""

import json

from actionarc.storage.arc_store import ArcStore


def test_arc_store_loads_all_json_files(tmp_path):
    first_arc = {
        "format_version": 1,
        "id": "first-arc",
        "name": "First Arc",
        "description": "",
        "enabled": True,
        "schedule": {"type": "manual"},
        "trigger": {"type": "always", "config": {}},
        "actions": [],
    }
    second_arc = {
        "format_version": 1,
        "id": "second-arc",
        "name": "Second Arc",
        "description": "",
        "enabled": False,
        "schedule": {"type": "manual"},
        "trigger": {"type": "always", "config": {}},
        "actions": [],
    }

    (tmp_path / "second.json").write_text(json.dumps(second_arc), encoding="utf-8")
    (tmp_path / "first.json").write_text(json.dumps(first_arc), encoding="utf-8")
    (tmp_path / "ignore.txt").write_text("Not an Arc.", encoding="utf-8")

    arcs = ArcStore().load_all(tmp_path)

    assert [arc.id for arc in arcs] == ["first-arc", "second-arc"]
    assert arcs[1].enabled is False