"""Resolve ActionArc resource and user-data paths."""

from importlib.resources import files
from pathlib import Path
from shutil import copyfileobj

from PySide6.QtCore import QStandardPaths


DEFAULT_ARC_DIRECTORY = files("actionarc").joinpath("data", "arcs")


def app_data_directory() -> Path:
    """Return the writable ActionArc application-data directory."""
    return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))


def prepare_arc_directory() -> Path:
    """Create the writable Arc directory and seed defaults when empty."""
    arc_directory = app_data_directory() / "arcs"
    arc_directory.mkdir(parents=True, exist_ok=True)

    if not any(arc_directory.glob("*.json")):
        for source_path in DEFAULT_ARC_DIRECTORY.iterdir():
            if not source_path.is_file() or not source_path.name.lower().endswith(".json"):
                continue

            with source_path.open("rb") as source, (arc_directory / source_path.name).open("wb") as destination:
                copyfileobj(source, destination)

    return arc_directory


def prepare_file_directory() -> Path:
    """Create and return the writable ActionArc file-output directory."""
    file_directory = app_data_directory() / "files"
    file_directory.mkdir(parents=True, exist_ok=True)
    return file_directory