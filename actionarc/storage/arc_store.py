"""Load and save ActionArc definitions."""

import json
from pathlib import Path

from actionarc.models import Arc


class ArcStore:
    """Load and save Arc definitions while preserving source paths."""

    def __init__(self):
        self._paths: dict[str, Path] = {}

    def load(self, path: str | Path) -> Arc:
        path = Path(path)

        with path.open("r", encoding="utf-8") as file:
            arc = Arc.from_dict(json.load(file))

        self._paths[arc.id] = path
        return arc

    def load_all(self, directory: str | Path) -> list[Arc]:
        directory = Path(directory)
        return [self.load(path) for path in sorted(directory.glob("*.json"))]

    def save(self, arc: Arc, path: str | Path | None = None) -> None:
        if path is None:
            path = self._paths.get(arc.id)

            if path is None:
                raise ValueError(f"Arc has no storage path: {arc.id}")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(arc.to_dict(), file, indent=2)
            file.write("\n")

        self._paths[arc.id] = path