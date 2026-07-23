"""Load and save ActionArc definitions."""

import json
from pathlib import Path

from actionarc.models import Arc


class ArcStore:
    """Loads and saves Arc definitions."""

    def load(self, path: str | Path) -> Arc:
        path = Path(path)

        with path.open("r", encoding="utf-8") as file:
            return Arc.from_dict(json.load(file))

    def load_all(self, directory: str | Path) -> list[Arc]:
        directory = Path(directory)
        return [self.load(path) for path in sorted(directory.glob("*.json"))]

    def save(self, arc: Arc, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(arc.to_dict(), file, indent=2)
            file.write("\n")