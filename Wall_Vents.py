# Wall_Vents.py

from typing import Any, Dict, List

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QLineEdit,
    QLabel,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Qt
from namelist_definitions import NAMELISTS
from tab_base import parse_namelist_value

class VentEntryWidget(QGroupBox):
    """Widget that captures one VENT entry."""

    def __init__(self, defaults: Dict[str, Dict[str, Any]], remove_callback=None, preset: Dict[str, Any] = None):
        super().__init__("Vent Configuration")
        self.defaults = defaults
        self.remove_callback = remove_callback
        self.fields: Dict[str, QLineEdit] = {}

        from PySide6.QtWidgets import QFormLayout
        self.form = QFormLayout()

        entry_values = preset or {}
        for var_name, metadata in self.defaults.items():
            line_edit = QLineEdit()
            # Get value from preset, or fallback to default defined in namelist_definitions
            value = entry_values.get(var_name, metadata.get("default", ""))
            
            # Handle array types by joining with commas
            if isinstance(value, (list, tuple)):
                value = ", ".join(str(x) for x in value)
            
            line_edit.setText(str(value))
            self.form.addRow(f"{var_name}:", line_edit)
            self.fields[var_name] = line_edit

        # Ensure TYPE is set to 'WALL' for this specific tab's entries
        if "type" in self.fields:
            self.fields["type"].setText("WALL")

        self.delete_button = QPushButton("Remove Vent")
        self.delete_button.clicked.connect(self._trigger_removal)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.delete_button)

        wrapper = QVBoxLayout()
        wrapper.addLayout(self.form)
        wrapper.addLayout(bottom_layout)
        self.setLayout(wrapper)

    def _trigger_removal(self):
        if self.remove_callback:
            self.remove_callback(self)

    def get_values(self) -> Dict[str, Any]:
        """Parses the text from fields back into the appropriate Fortran types."""
        values = {}
        for var_name, widget in self.fields.items():
            meta = self.defaults[var_name]
            values[var_name] = parse_namelist_value(widget.text(), meta)
        return values


class Wall_Vents(QWidget):
    """Tab that allows adding, editing, and removing VENT namelist entries where TYPE='WALL'."""

    def __init__(self, parent=None):
        super().__init__(parent)
        outer_layout = QVBoxLayout(self)

        header = QLabel("Wall Vents (VENT TYPE='WALL')")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-weight: bold; font-size: 14pt;")
        outer_layout.addWidget(header)

        # Scroll area to handle many vent entries
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.entries_layout = QVBoxLayout(container)
        self.entries_layout.addStretch()  # Keep entries at the top
        self.scroll.setWidget(container)
        outer_layout.addWidget(self.scroll)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Wall Vent")
        self.add_button.clicked.connect(self._add_empty_entry)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        outer_layout.addLayout(button_layout)

        self.entry_widgets: List[VentEntryWidget] = []
        self._add_empty_entry()  # Initialize with one empty entry

    def _add_empty_entry(self):
        self._add_entry(preset={"type": "WALL"})

    def _add_entry(self, preset: Dict[str, Any] = None):
        """Create a new vent entry widget and add it to the layout."""
        entry_widget = VentEntryWidget(
            defaults=NAMELISTS["VENT"],
            preset=preset,
            remove_callback=self._remove_entry,
        )
        self.entry_widgets.append(entry_widget)
        # Insert before the stretch spacer at the bottom
        self.entries_layout.insertWidget(self.entries_layout.count() - 1, entry_widget)

    def _remove_entry(self, widget: VentEntryWidget, *, force: bool = False):
        """Removes a vent entry, ensuring at least one remains unless forced."""
        if not force and len(self.entry_widgets) == 1:
            QMessageBox.information(self, "Cannot remove", "At least one VENT entry is required.")
            return
        self.entry_widgets.remove(widget)
        widget.setParent(None)
        widget.deleteLater()

    def _clear_entries(self):
        """Removes all current entry widgets."""
        for widget in list(self.entry_widgets):
            self._remove_entry(widget, force=True)

    def get_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Returns a dictionary containing a list of all VENT record data for this tab."""
        return {"VENT": [entry.get_values() for entry in self.entry_widgets]}

    def set_data(self, data: Dict[str, Any]):
        """Populates the tab ONLY with VENT records where TYPE='WALL' (case-insensitive)."""
        all_vents = data.get("VENT", [])
        
        # Handle case where only a single dict is provided instead of a list
        if isinstance(all_vents, dict):
            all_vents = [all_vents]
        
        # Filter for TYPE='WALL'
        wall_vents = [
            v for v in all_vents 
            if str(v.get("type", "")).strip().upper() == "WALL"
        ]
        
        self._clear_entries()
        
        if not wall_vents:
            self._add_empty_entry()
        else:
            for entry in wall_vents:
                self._add_entry(preset=entry)
