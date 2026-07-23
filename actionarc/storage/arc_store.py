"""Load and save ActionArc definitions."""

import json
from pathlib import Path

from actionarc.models import Arc


class ArcStore:
    """Loads and saves Arc definitions."""

    def load(self, path: str | Path) -> Arc:
        """Load one Arc from a JSON file."""
        path = Path(path)

        with path.open("r", encoding="utf-8") as file:
            return Arc.from_dict(json.load(file))

    def load_all(self, directory: str | Path) -> list[Arc]:
        """Load every Arc JSON file from a directory."""
        directory = Path(directory)
        return [self.load(path) for path in sorted(directory.glob("*.json"))]

    def save(self, arc: Arc, path: str | Path) -> None:
        raise NotImplementedError("Saving Arcs will be implemented later.")