"""Action that writes text to a file."""

from pathlib import Path
from typing import Any

from actionarc.components.actions.base import Action
from actionarc.engine.context import RunContext
from actionarc.engine.results import ActionResult
from actionarc.paths import prepare_file_directory


class WriteFileAction(Action):
    """Write configured text to a file."""

    component_id  = "write_file"

    def __init__(self, config: dict[str, Any]):
        self.config = config

    def execute(self, context: RunContext) -> ActionResult:
        path = Path(self.config["path"])

        if not path.is_absolute():
            path = prepare_file_directory() / path

        content = self.config.get("content", "")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        return ActionResult(succeeded=True, message=f"Wrote file: {path}")