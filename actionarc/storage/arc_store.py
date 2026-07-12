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

    def save(self, arc: Arc, path: str | Path) -> None:
        raise NotImplementedError("Saving Arcs will be implemented later.")