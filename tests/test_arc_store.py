"""Tests for Arc persistence."""

from actionarc.models import Arc
from actionarc.storage.arc_store import ArcStore


def test_arc_can_be_saved_and_reloaded(tmp_path) -> None:
    source_path = tmp_path / "source.json"
    saved_path = tmp_path / "saved.json"

    source_path.write_text(
        """
{
  "format_version": 1,
  "id": "test-arc",
  "name": "Test Arc",
  "description": "Tests Arc persistence.",
  "enabled": true,
  "schedule": {
    "type": "interval",
    "seconds": 5
  },
  "trigger": {
    "type": "always",
    "config": {}
  },
  "actions": [
    {
      "type": "write_file",
      "config": {
        "path": "data/test-output.txt",
        "content": "Test complete."
      }
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    store = ArcStore()
    original = store.load(source_path)

    store.save(original, saved_path)

    reloaded = store.load(saved_path)

    assert isinstance(reloaded, Arc)
    assert reloaded == original
    assert reloaded.to_dict() == original.to_dict()

def test_save_uses_loaded_arc_source_path(tmp_path):
    source_path = tmp_path / "Jons export 122226.json"
    source_path.write_text(
        """
{
  "format_version": 1,
  "id": "imported-arc",
  "name": "Imported Arc",
  "description": "",
  "enabled": true,
  "schedule": {
    "type": "manual"
  },
  "trigger": {
    "type": "always",
    "config": {}
  },
  "actions": []
}
""".strip(),
        encoding="utf-8",
    )

    store = ArcStore()
    arc = store.load(source_path)
    arc.enabled = False

    store.save(arc)

    reloaded = ArcStore().load(source_path)

    assert reloaded.enabled is False
    assert list(tmp_path.glob("*.json")) == [source_path]