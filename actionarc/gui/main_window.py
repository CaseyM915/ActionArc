"""Main ActionArc application window."""

from datetime import datetime
from pathlib import Path
from threading import Thread
from uuid import uuid4
import re

from PySide6.QtCore import QObject, QSize, Qt, Signal
from PySide6.QtGui import QColor, QCloseEvent
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from actionarc.engine.controller import EngineController
from actionarc.engine.results import ArcRunResult, ArcRunStatus
from actionarc import APP_VERSION
from actionarc.models import ActionDefinition, Arc, ScheduleDefinition, TriggerDefinition
from actionarc.storage.arc_store import ArcStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGO_PATH = PROJECT_ROOT / "assets" / "AA.svg"
ARCS_PATH = PROJECT_ROOT / "actionarc" / "data" / "arcs"


class EngineSignalBridge(QObject):
    """Move engine callbacks safely onto the Qt GUI thread."""

    result_received = Signal(object, object)
    manual_run_finished = Signal()
    operation_failed = Signal(str)

    def publish_result(self, arc: Arc, result: ArcRunResult) -> None:
        """Publish an engine result through a Qt signal."""
        self.result_received.emit(arc, result)

class ToggleSwitch(QCheckBox):
    """Display a checkbox as a toggle switch."""

    def __init__(self, text: str = ""):
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("toggleSwitch")
        self.setFixedWidth(110)

class ArcListCard(QFrame):
    """Display one Arc inside the loaded Arc list."""

    def __init__(self, arc: Arc, schedule_text: str):
        super().__init__()

        self.setObjectName("arcCard")
        self.setProperty("selected", False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(7)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        name = QLabel(arc.name)
        name.setObjectName("arcCardName")

        status = QLabel("Enabled" if arc.enabled else "Disabled")
        status.setObjectName("arcCardStatus")
        status.setProperty("enabled", arc.enabled)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        action_names = ", ".join(action.type for action in arc.actions) or "No actions"

        details_row = QHBoxLayout()
        details_row.setSpacing(10)

        flow = QLabel(f"{arc.trigger.type}  →  {action_names}")
        flow.setObjectName("arcCardFlow")

        schedule = QLabel(f"◷  {schedule_text}")
        schedule.setObjectName("arcCardSchedule")

        title_row.addWidget(name, 1)
        title_row.addWidget(status)

        details_row.addWidget(flow)
        details_row.addStretch()
        details_row.addWidget(schedule)

        layout.addLayout(title_row)
        layout.addLayout(details_row)

    def set_selected(self, selected: bool) -> None:
        """Update the card's selected appearance."""
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)


class MainWindow(QMainWindow):
    """Display and control the current ActionArc engine."""

    def __init__(self, controller: EngineController, arcs: list[Arc], arc_store: ArcStore, signals: EngineSignalBridge,):
        super().__init__()

        self.controller = controller
        self.arcs = arcs
        self.arc_store = arc_store
        self.signals = signals
        self.manual_run_active = False

        self.setWindowTitle("ActionArc")
        self.resize(1180, 760)
        self.setMinimumSize(900, 620)

        self._build_window()
        self._connect_signals()
        self._load_arcs()
        self._update_engine_status()
        self._add_activity("ActionArc is ready.")

    def _build_window(self) -> None:
        """Create the main window layout and controls."""
        central_widget = QWidget()
        central_widget.setObjectName("applicationBackground")

        page_layout = QVBoxLayout(central_widget)
        page_layout.setContentsMargins(26, 22, 26, 26)
        page_layout.setSpacing(18)

        page_layout.addWidget(self._build_header())
        page_layout.addWidget(self._build_content(), 1)
        page_layout.addWidget(self._build_activity_panel())

        self.setCentralWidget(central_widget)
        self.setStyleSheet(self._stylesheet())

    def _build_header(self) -> QWidget:
        """Create the ActionArc application header."""
        header = QWidget()
        header.setObjectName("header")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        logo = QSvgWidget(str(LOGO_PATH))
        logo.setFixedSize(48, 48)

        title_area = QVBoxLayout()
        title_area.setSpacing(1)

        title = QLabel("ActionArc")
        title.setObjectName("applicationTitle")

        subtitle = QLabel(f"Your automations at a glance.  •  v{APP_VERSION}")
        subtitle.setObjectName("mutedText")

        title_area.addWidget(title)
        title_area.addWidget(subtitle)

        self.engine_status = QLabel()
        self.engine_status.setObjectName("engineStatus")
        self.engine_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.engine_status.setMinimumWidth(160)

        layout.addWidget(logo)
        layout.addLayout(title_area)
        layout.addStretch()
        layout.addWidget(self.engine_status)

        return header

    def _build_content(self) -> QWidget:
        """Create the Arc list and selected Arc details."""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        splitter.addWidget(self._build_arc_panel())
        splitter.addWidget(self._build_details_panel())
        splitter.setSizes([430, 700])

        return splitter

    def _build_arc_panel(self) -> QWidget:
        """Create the loaded Arc list and engine controls."""
        panel = QFrame()
        panel.setObjectName("panel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        heading_row = QHBoxLayout()

        heading_area = QVBoxLayout()
        heading_area.setSpacing(2)

        heading = QLabel("Arcs")
        heading.setObjectName("sectionTitle")

        subtitle = QLabel("Loaded automations")
        subtitle.setObjectName("mutedText")

        heading_area.addWidget(heading)
        heading_area.addWidget(subtitle)

        self.arc_count = QLabel()
        self.arc_count.setObjectName("countBadge")
        self.arc_count.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.new_arc_button = QPushButton("+  New Arc")
        self.new_arc_button.setObjectName("newArcButton")

        heading_row.addLayout(heading_area)
        heading_row.addStretch()
        heading_row.addWidget(self.arc_count)
        heading_row.addWidget(self.new_arc_button)

        self.arc_list = QListWidget()
        self.arc_list.setObjectName("arcList")
        self.arc_list.setSpacing(7)
        self.arc_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        button_layout = QHBoxLayout()
        button_layout.setSpacing(9)

        self.start_button = QPushButton("Start Engine")
        self.stop_button = QPushButton("Stop Engine")
        self.run_button = QPushButton("▶  Run Now")

        self.start_button.setObjectName("startButton")
        self.stop_button.setObjectName("secondaryButton")
        self.run_button.setObjectName("primaryButton")

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_layout.addWidget(self.run_button)

        layout.addLayout(heading_row)
        layout.addWidget(self.arc_list, 1)
        layout.addLayout(button_layout)

        return panel

    def _build_details_panel(self) -> QWidget:
        """Create the selected Arc overview panel."""
        panel = QFrame()
        panel.setObjectName("panel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(16)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        title_area = QVBoxLayout()
        title_area.setSpacing(5)

        self.arc_name = QLabel("Select an Arc")
        self.arc_name.setObjectName("arcTitle")

        self.arc_description = QLabel("Select a loaded Arc to view its details.")
        self.arc_description.setObjectName("mutedText")
        self.arc_description.setWordWrap(True)

        title_area.addWidget(self.arc_name)
        title_area.addWidget(self.arc_description)

        self.arc_enabled_toggle = ToggleSwitch("Enabled")
        self.arc_enabled_toggle.setEnabled(False)

        self.duplicate_arc_button = QPushButton("Duplicate")
        self.duplicate_arc_button.setObjectName("secondaryButton")
        self.duplicate_arc_button.setEnabled(False)

        title_controls = QVBoxLayout()
        title_controls.setSpacing(8)
        title_controls.addWidget(self.arc_enabled_toggle)

        title_row.addLayout(title_area, 1)
        title_row.addLayout(title_controls)

        overview_row = QHBoxLayout()

        overview_heading = QLabel("Overview")
        overview_heading.setObjectName("subsectionTitle")

        overview_row.addWidget(overview_heading)
        overview_row.addStretch()
        overview_row.addWidget(self.duplicate_arc_button)

        summary_card = QFrame()
        summary_card.setObjectName("summaryCard")

        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(18, 16, 18, 16)
        summary_layout.setSpacing(0)

        self.arc_trigger = self._create_detail_row("Trigger")
        self.arc_actions = self._create_detail_row("Action")
        self.arc_schedule = self._create_detail_row("Schedule")
        self.arc_status = self._create_detail_row("Status")

        summary_layout.addWidget(self.arc_trigger)
        summary_layout.addWidget(self._create_separator())
        summary_layout.addWidget(self.arc_actions)
        summary_layout.addWidget(self._create_separator())
        summary_layout.addWidget(self.arc_schedule)
        summary_layout.addWidget(self._create_separator())
        summary_layout.addWidget(self.arc_status)

        layout.addLayout(title_row)
        layout.addLayout(overview_row)
        layout.addWidget(summary_card)
        layout.addStretch()

        return panel

    def _build_activity_panel(self) -> QWidget:
        """Create the recent activity area."""
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumHeight(215)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 17, 20, 18)
        layout.setSpacing(11)

        heading_row = QHBoxLayout()

        heading = QLabel("Recent Activity")
        heading.setObjectName("sectionTitle")

        activity_hint = QLabel("Newest activity appears first")
        activity_hint.setObjectName("mutedText")

        heading_row.addWidget(heading)
        heading_row.addStretch()
        heading_row.addWidget(activity_hint)

        self.activity_log = QListWidget()
        self.activity_log.setObjectName("activityLog")
        self.activity_log.setSpacing(2)
        self.activity_log.setSelectionMode(
            QListWidget.SelectionMode.NoSelection
        )

        layout.addLayout(heading_row)
        layout.addWidget(self.activity_log)

        return panel

    def _create_detail_row(self, label_text: str) -> QLabel:
        """Create a reusable Arc overview row."""
        label = QLabel(f"<b>{label_text}</b>")
        label.setObjectName("detailRow")
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        label.setMinimumHeight(46)
        return label

    def _create_separator(self) -> QFrame:
        """Create a divider between overview rows."""
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        return separator

    def _connect_signals(self) -> None:
        """Connect buttons and engine events to window behavior."""
        self.start_button.clicked.connect(self._start_engine)
        self.stop_button.clicked.connect(self._stop_engine)
        self.run_button.clicked.connect(self._run_selected_arc)
        self.new_arc_button.clicked.connect(self._create_arc)
        self.arc_enabled_toggle.toggled.connect(self._set_selected_arc_enabled)
        self.arc_list.currentItemChanged.connect(self._show_selected_arc)

        self.signals.result_received.connect(self._handle_result)
        self.signals.manual_run_finished.connect(self._finish_manual_run)
        self.signals.operation_failed.connect(self._handle_operation_error)
        self.duplicate_arc_button.clicked.connect(self._duplicate_selected_arc)

    def _load_arcs(self) -> None:
        """Populate the Arc list from the loaded Arcs."""
        self.arc_list.clear()

        for arc in self.arcs:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, arc.id)
            item.setToolTip(arc.description)
            item.setSizeHint(QSize(0, 78))

            card = ArcListCard(
                arc=arc,
                schedule_text=self._format_schedule(arc),
            )

            self.arc_list.addItem(item)
            self.arc_list.setItemWidget(item, card)

        self.arc_count.setText(str(len(self.arcs)))

        if self.arc_list.count():
            self.arc_list.setCurrentRow(0)

    def _show_selected_arc(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        """Display details for the selected Arc."""
        self._set_card_selected(previous, False)
        self._set_card_selected(current, True)

        if current is None:
            self.arc_enabled_toggle.blockSignals(True)
            self.arc_enabled_toggle.setChecked(False)
            self.arc_enabled_toggle.setEnabled(False)
            self.arc_enabled_toggle.blockSignals(False)
            self.duplicate_arc_button.setEnabled(False)
            self._update_run_button()
            return

        arc = self._find_arc(current.data(Qt.ItemDataRole.UserRole))

        if arc is None:
            return

        action_names = ", ".join(
            action.type for action in arc.actions
        ) or "None"

        self.arc_name.setText(arc.name)
        self.arc_description.setText(
            arc.description or "No description provided."
        )

        self.arc_enabled_toggle.blockSignals(True)
        self.arc_enabled_toggle.setChecked(arc.enabled)
        self.arc_enabled_toggle.setText("Enabled" if arc.enabled else "Disabled")
        self.arc_enabled_toggle.setEnabled(True)
        self.arc_enabled_toggle.blockSignals(False)
        self.duplicate_arc_button.setEnabled(True)

        self.arc_trigger.setText(
            f"<b>Trigger</b><br>"
            f"<span style='color: #f0f6fc;'>{arc.trigger.type}</span>"
        )

        self.arc_actions.setText(
            f"<b>Action</b><br>"
            f"<span style='color: #f0f6fc;'>{action_names}</span>"
        )

        self.arc_schedule.setText(
            f"<b>Schedule</b><br>"
            f"<span style='color: #f0f6fc;'>"
            f"{self._format_schedule(arc)}</span>"
        )

        self.arc_status.setText(
            f"<b>Status</b><br>"
            f"<span style='color: #f0f6fc;'>"
            f"{'Enabled' if arc.enabled else 'Disabled'}</span>"
        )

        self._update_run_button()

    def _start_engine(self) -> None:
        """Start the scheduler through EngineController."""
        if self.controller.is_running:
            return

        self.controller.start()
        self._update_engine_status()
        self._add_activity("Engine started.", "success")

    def _stop_engine(self) -> None:
        """Stop the scheduler through EngineController."""
        if not self.controller.is_running:
            return

        self.controller.stop()
        self._update_engine_status()
        self._add_activity("Engine stopped.")

    def _set_selected_arc_enabled(self, enabled: bool) -> None:
        """Update the selected Arc's enabled state and persist the change."""
        arc = self._selected_arc()

        if arc is None:
            self.arc_enabled_toggle.blockSignals(True)
            self.arc_enabled_toggle.setChecked(False)
            self.arc_enabled_toggle.blockSignals(False)
            return

        if arc.enabled == enabled:
            return

        arc.enabled = enabled
        self.arc_enabled_toggle.setText("Enabled" if enabled else "Disabled")

        try:
            self.arc_store.save(arc)
        except Exception as error:
            arc.enabled = not enabled
            self.arc_enabled_toggle.blockSignals(True)
            self.arc_enabled_toggle.setChecked(arc.enabled)
            self.arc_enabled_toggle.setText("Enabled" if arc.enabled else "Disabled")
            self.arc_enabled_toggle.blockSignals(False)
            self._add_activity(f"Could not update {arc.name}: {error}", "failure")
            return

        self._refresh_selected_arc()
        state = "enabled" if enabled else "disabled"
        self._add_activity(f"{arc.name} was {state}.", "success")

    def _create_arc(self) -> None:
        """Create a new Arc with default settings."""
        arc = Arc(
            format_version=1,
            id=str(uuid4()),
            name="New Arc",
            description="",
            enabled=False,
            schedule=ScheduleDefinition(type="manual"),
            trigger=TriggerDefinition(type="always"),
            actions=[
                ActionDefinition(
                    type="write_file",
                    config={
                        "path": "data/new-arc-output.txt",
                        "content": "Hello from ActionArc!",
                    },
                )
            ],
        )

        self.arc_store.save(arc, ARCS_PATH / f"{arc.id}.json")
        self.arcs.append(arc)
        self._load_arcs()

        for row in range(self.arc_list.count()):
            item = self.arc_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == arc.id:
                self.arc_list.setCurrentItem(item)
                break

        self._add_activity(f'Created Arc "{arc.name}".')

    def _duplicate_selected_arc(self) -> None:
        """Duplicate the selected Arc as a disabled independent copy."""
        source_arc = self._selected_arc()

        if source_arc is None:
            return

        arc_data = source_arc.to_dict()
        arc_data["id"] = str(uuid4())
        arc_data["name"] = self._next_copy_name(source_arc.name)
        arc_data["enabled"] = False

        arc = Arc.from_dict(arc_data)

        try:
            self.arc_store.save(arc, ARCS_PATH / f"{arc.id}.json")
        except Exception as error:
            self._add_activity(f"Could not duplicate {source_arc.name}: {error}", "failure")
            return

        self.arcs.append(arc)
        self._load_arcs()

        for row in range(self.arc_list.count()):
            item = self.arc_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == arc.id:
                self.arc_list.setCurrentItem(item)
                break

        self._add_activity(f'Duplicated Arc as "{arc.name}".', "success")

    def _run_selected_arc(self) -> None:
        """Run the selected Arc without blocking the GUI thread."""
        arc = self._selected_arc()

        if arc is None:
            self._add_activity("No Arc is selected.", "warning")
            return

        self.manual_run_active = True
        self._update_run_button()
        self._add_activity(f"Manual run started: {arc.name}")

        Thread(
            target=self._run_arc_worker,
            args=(arc.id,),
            daemon=True,
            name=f"ActionArcManualRun-{arc.id}",
        ).start()

    def _run_arc_worker(self, arc_id: str) -> None:
        """Execute a manual Arc run on a background thread."""
        try:
            self.controller.run_arc_by_id(arc_id)
        except Exception as error:
            self.signals.operation_failed.emit(str(error))
        finally:
            self.signals.manual_run_finished.emit()

    def _finish_manual_run(self) -> None:
        """Restore the Run Now button after a manual run."""
        self.manual_run_active = False
        self._update_run_button()

    def _handle_result(self, arc: Arc, result: ArcRunResult) -> None:
        """Display a completed Arc result."""
        status_text = result.status.value.replace("_", " ").title()
        message = self._result_message(result)

        tone = "normal"

        if result.status == ArcRunStatus.SUCCEEDED:
            tone = "success"
        elif result.status == ArcRunStatus.FAILED:
            tone = "failure"
        elif result.status == ArcRunStatus.NOT_TRIGGERED:
            tone = "warning"

        self._add_activity(
            f"{arc.name} — {status_text}: {message}",
            tone,
        )

    def _handle_operation_error(self, message: str) -> None:
        """Display an unexpected engine operation error."""
        self._add_activity(
            f"Manual run failed: {message}",
            "failure",
        )

    def _result_message(self, result: ArcRunResult) -> str:
        """Choose the most useful message from an Arc result."""
        if result.status == ArcRunStatus.NOT_TRIGGERED:
            return result.trigger.message or "Trigger did not match."

        failed_action = next(
            (
                action
                for action in result.actions
                if not action.succeeded
            ),
            None,
        )

        if failed_action:
            return failed_action.message or "An action failed."

        successful_action = next(
            (
                action
                for action in reversed(result.actions)
                if action.succeeded and action.message
            ),
            None,
        )

        if successful_action:
            return successful_action.message

        if result.status == ArcRunStatus.SUCCEEDED:
            return "Arc completed successfully."

        return "Arc execution failed."

    def _set_card_selected(
        self,
        item: QListWidgetItem | None,
        selected: bool,
    ) -> None:
        """Update the selected appearance of an Arc card."""
        if item is None:
            return

        card = self.arc_list.itemWidget(item)

        if isinstance(card, ArcListCard):
            card.set_selected(selected)

    def _refresh_selected_arc(self) -> None:
        """Refresh the selected Arc card and detail panel."""
        item = self.arc_list.currentItem()
        arc = self._selected_arc()

        if item is None or arc is None:
            return

        card = ArcListCard(arc, self._format_schedule(arc))
        self.arc_list.setItemWidget(item, card)
        card.set_selected(True)
        self._show_selected_arc(item, None)

    def _selected_arc(self) -> Arc | None:
        """Return the Arc represented by the selected list item."""
        item = self.arc_list.currentItem()

        if item is None:
            return None

        return self._find_arc(
            item.data(Qt.ItemDataRole.UserRole)
        )

    def _find_arc(self, arc_id: str) -> Arc | None:
        """Find a loaded Arc by ID."""
        return next(
            (arc for arc in self.arcs if arc.id == arc_id),
            None,
        )

    def _next_copy_name(self, name: str) -> str:
        """Return the next available copy name for an Arc."""
        base_name = re.sub(r" \(Copy(?: \d+)?\)$", "", name)
        existing_names = {arc.name for arc in self.arcs}

        if f"{base_name} (Copy)" not in existing_names:
            return f"{base_name} (Copy)"

        copy_number = 2
        while f"{base_name} (Copy {copy_number})" in existing_names:
            copy_number += 1

        return f"{base_name} (Copy {copy_number})"

    def _format_schedule(self, arc: Arc) -> str:
        """Create a readable schedule description."""
        if arc.schedule.type == "interval":
            seconds = arc.schedule.config.get("seconds")
            return f"Every {seconds} seconds"

        return arc.schedule.type.replace("_", " ").title()

    def _update_engine_status(self) -> None:
        """Update the status badge and engine controls."""
        is_running = self.controller.is_running

        self.engine_status.setText(
            "●  Engine Running"
            if is_running
            else "●  Engine Stopped"
        )

        self.engine_status.setProperty(
            "running",
            is_running,
        )

        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)

        self.engine_status.style().unpolish(self.engine_status)
        self.engine_status.style().polish(self.engine_status)

    def _update_run_button(self) -> None:
        """Enable Run Now when an Arc is selected and no manual run is active."""
        self.run_button.setEnabled(
            self._selected_arc() is not None
            and not self.manual_run_active
        )

    def _add_activity(
        self,
        message: str,
        tone: str = "normal",
    ) -> None:
        """Add a timestamped entry to recent activity."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        item = QListWidgetItem(f"{timestamp}    {message}")

        tone_colors = {
            "normal": QColor("#c9d1d9"),
            "success": QColor("#3fb950"),
            "warning": QColor("#d29922"),
            "failure": QColor("#f85149"),
        }

        item.setForeground(tone_colors[tone])
        item.setSizeHint(QSize(0, 30))

        self.activity_log.insertItem(0, item)
        self.activity_log.scrollToTop()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Stop the engine before closing the application."""
        if self.controller.is_running:
            self.controller.stop()

        event.accept()

    @staticmethod
    def _stylesheet() -> str:
        """Return the initial ActionArc visual theme."""
        return """
            QMainWindow {
                background-color: #070d14;
            }

            QWidget#applicationBackground {
                background-color: #070d14;
                color: #e6edf3;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QLabel {
                background-color: transparent;
                border: none;
            }

            QLabel#applicationTitle {
                color: #dcecff;
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#sectionTitle {
                color: #f0f6fc;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#subsectionTitle {
                color: #f0f6fc;
                font-size: 15px;
                font-weight: 650;
            }

            QLabel#arcTitle {
                color: #f0f6fc;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#mutedText {
                color: #8b949e;
            }

            QLabel#countBadge {
                color: #79c0ff;
                background-color: #0d2847;
                border: 1px solid #1f4c7a;
                border-radius: 12px;
                min-width: 26px;
                padding: 4px 8px;
                font-weight: 700;
            }

            QLabel#engineStatus {
                color: #f85149;
                background-color: #1b222c;
                border: 1px solid #303b49;
                border-radius: 16px;
                padding: 10px 16px;
                font-weight: 650;
            }

            QLabel#engineStatus[running="true"] {
                color: #3fb950;
                background-color: #10291c;
                border-color: #1d5133;
            }

            QLabel#engineStatus[running="false"] {
                color: #f85149;
                background-color: #30171b;
                border-color: #61252c;
            }

            QCheckBox#toggleSwitch {
                spacing: 10px;
                color: #f0f6fc;
                font-weight: 650;
            }
            
            QCheckBox#toggleSwitch::indicator {
                width: 38px;
                height: 20px;
                border: 1px solid #45566a;
                border-radius: 10px;
                background-color: #202833;
            }
            
            QCheckBox#toggleSwitch::indicator:hover {
                border-color: #6e8196;
            }
            
            QCheckBox#toggleSwitch::indicator:checked {
                background-color: #238636;
                border-color: #3fb950;
            }
            
            QCheckBox#toggleSwitch::indicator:disabled {
                background-color: #101821;
                border-color: #1d2a38;
            }

            QFrame#panel {
                background-color: #0c1621;
                border: 1px solid #1d2a38;
                border-radius: 11px;
            }

            QFrame#summaryCard {
                background-color: #09121b;
                border: 1px solid #1d2a38;
                border-radius: 9px;
            }

            QFrame#separator {
                color: #1d2a38;
                background-color: #1d2a38;
                border: none;
                max-height: 1px;
            }

            QLabel#detailRow {
                color: #8b949e;
                padding: 7px 2px;
            }

            QListWidget#arcList,
            QListWidget#activityLog {
                color: #e6edf3;
                background-color: #08111a;
                border: 1px solid #1d2a38;
                border-radius: 8px;
                padding: 7px;
                outline: none;
            }

            QListWidget#arcList::item {
                background-color: transparent;
                border: none;
                padding: 0;
            }

            QListWidget#arcList::item:selected {
                background-color: transparent;
                border: none;
            }

            QFrame#arcCard {
                background-color: #0d1823;
                border: 1px solid #1d2a38;
                border-radius: 8px;
            }

            QFrame#arcCard:hover {
                background-color: #122337;
                border-color: #28547e;
            }

            QFrame#arcCard[selected="true"] {
                background-color: #102c4c;
                border: 1px solid #2f81f7;
            }

            QLabel#arcCardName {
                color: #f0f6fc;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#arcCardFlow {
                color: #c9d1d9;
                font-size: 13px;
            }

            QLabel#arcCardSchedule {
                color: #8b949e;
                font-size: 12px;
            }

            QLabel#arcCardStatus {
                min-width: 58px;
                color: #8b949e;
                background-color: #202833;
                border: 1px solid #303b49;
                border-radius: 9px;
                padding: 3px 7px;
                font-size: 11px;
                font-weight: 650;
            }

            QLabel#arcCardStatus[enabled="true"] {
                color: #3fb950;
                background-color: #10291c;
                border-color: #1d5133;
            }

            QLabel#arcCardStatus[enabled="false"] {
                color: #8b949e;
                background-color: #202833;
                border-color: #303b49;
            }

            QListWidget#activityLog::item {
                border: none;
                padding: 4px 7px;
            }

            QPushButton {
                color: #e6edf3;
                background-color: #16202c;
                border: 1px solid #303b49;
                border-radius: 7px;
                padding: 10px 14px;
                font-weight: 650;
            }

            QPushButton:hover {
                background-color: #202d3b;
                border-color: #45566a;
            }

            QPushButton:pressed {
                background-color: #101821;
            }

            QPushButton:disabled {
                color: #52606f;
                background-color: #101821;
                border-color: #1d2a38;
            }

            QPushButton#primaryButton {
                color: white;
                background-color: #1f6feb;
                border-color: #388bfd;
            }

            QPushButton#primaryButton:hover {
                background-color: #2f81f7;
            }

            QPushButton#startButton {
                color: #56d364;
                background-color: #10291c;
                border-color: #1d5133;
            }

            QPushButton#startButton:hover {
                background-color: #163823;
            }

            QPushButton#primaryButton:disabled,
            QPushButton#startButton:disabled,
            QPushButton#secondaryButton:disabled {
                color: #52606f;
                background-color: #101821;
                border-color: #1d2a38;
            }

            QSplitter::handle {
                background-color: transparent;
                width: 12px;
            }

            QScrollBar:vertical {
                background-color: transparent;
                width: 10px;
                margin: 3px;
            }

            QScrollBar::handle:vertical {
                background-color: #303b49;
                border-radius: 4px;
                min-height: 25px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #45566a;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """