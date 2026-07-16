"""Build and launch the ActionArc desktop application."""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from actionarc.components.builtin import register_builtin_components
from actionarc.components.registry import ComponentRegistry
from actionarc.engine.controller import EngineController
from actionarc.engine.runner import ArcRunner
from actionarc.gui.main_window import EngineSignalBridge, MainWindow
from actionarc.storage.arc_store import ArcStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ICON_PATH = PROJECT_ROOT / "assets" / "AA.svg"
EXAMPLE_ARC_PATH = PROJECT_ROOT / "data" / "arcs" / "example_arc.json"


def run_application() -> int:
    """Create the application services and launch the main window."""
    app = QApplication(sys.argv)
    app.setApplicationName("ActionArc")
    app.setOrganizationName("SUDOMG")
    app.setWindowIcon(QIcon(str(APP_ICON_PATH)))

    registry = ComponentRegistry()
    register_builtin_components(registry)

    arc = ArcStore().load(EXAMPLE_ARC_PATH)
    signals = EngineSignalBridge()
    controller = EngineController(ArcRunner(registry), [arc], signals.publish_result)

    window = MainWindow(controller, [arc], signals)
    window.show()

    return app.exec()