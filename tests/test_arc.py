"""Tests for the Arc model."""

import pytest

from actionarc.models import Arc


def test_arc_loads_supported_format_version():
    data = {
        "format_version": 1,
        "id": "test-arc",
        "name": "Test Arc",
        "description": "",
        "enabled": True,
        "schedule": {"type": "manual"},
        "trigger": {"type": "always", "config": {}},
        "actions": [],
    }

    arc = Arc.from_dict(data)

    assert arc.format_version == 1
    assert arc.id == "test-arc"


def test_arc_rejects_unsupported_format_version():
    data = {
        "format_version": 999,
        "id": "test-arc",
        "name": "Test Arc",
        "description": "",
        "enabled": True,
        "schedule": {"type": "manual"},
        "trigger": {"type": "always", "config": {}},
        "actions": [],
    }

    with pytest.raises(ValueError, match="Unsupported Arc format version"):
        Arc.from_dict(data)