# Compartments.py

from typing import Any, Dict, List
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QFormLayout,
    QLineEdit,
    QLabel,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Qt
from namelist_definitions import NAMELISTS
from tab_base import parse_namelist_value

class CompartmentEntryWidget(QGroupBox):
    """Widget that captures one COMP (Compartment) entry."""

    def __init__(self, defaults: Dict[str, Dict[str, Any]], remove_callback=None, preset: Dict[str, Any] = None):
        super().__init__("Compartment Definition")
        self.defaults = defaults
        self.remove_callback = remove_callback
        self.form = QFormLayout()
        self.fields: Dict[str, QLineEdit] = {}

        entry_values = preset or {}
        # Iterate through the COMP namelist definition to create fields
        for var_name, metadata in self.defaults.items():
            line_edit = QLineEdit()
            # Get value from preset, fallback to default
            val = entry_values.get(var_name, metadata.get("default", ""))
            
            # Format arrays as comma-separated strings for the UI
            if isinstance(val, (list, tuple)):
                val = ", ".join(str(x) for x in val)
            
            line_edit.setText(str(val))
            self.form.addRow(f"{var_name}:", line_edit)
            self.fields[var_name] = line_edit

        self.delete_button = QPushButton("Remove Compartment")
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
        """Parse UI fields back into namelist-compatible Python types."""
        values = {}
        for var_name, widget in self.fields.items():
            meta = self.defaults[var_name]
            values[var_name] = parse_namelist_value(widget.text(), meta)
        return values

    def set_values(self, values: Dict[str, Any]):
        """Update UI fields with provided values."""
        for var_name, widget in self.fields.items():
            incoming = values.get(var_name, self.defaults[var_name].get("default", ""))
            if isinstance(incoming, (list, tuple)):
                incoming = ", ".join(str(x) for x in incoming)
            widget.setText(str(incoming))


class Compartments(QWidget):
    """Tab that allows adding, editing, and removing multiple COMP namelist entries."""

    def __init__(self, parent=None):
        super().__init__(parent)
        outer_layout = QVBoxLayout(self)

        header = QLabel("Compartment Properties (COMP)")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-weight: bold; font-size: 14pt;")
        outer_layout.addWidget(header)

        # Scroll area to handle many compartment entries
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.entries_layout = QVBoxLayout(container)
        self.entries_layout.addStretch() # Push entries to the top
        self.scroll.setWidget(container)
        outer_layout.addWidget(self.scroll)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Compartment")
        self.add_button.clicked.connect(self._add_empty_entry)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        outer_layout.addLayout(button_layout)

        self.entry_widgets: List[CompartmentEntryWidget] = []
        self._add_empty_entry()  # Initialize with one entry

    def _add_empty_entry(self):
        self._add_entry()

    def _add_entry(self, preset: Dict[str, Any] = None):
        """Create a new compartment entry widget and add it to the layout."""
        entry_widget = CompartmentEntryWidget(
            defaults=NAMELISTS["COMP"],
            preset=preset,
            remove_callback=self._remove_entry,
        )
        self.entry_widgets.append(entry_widget)
        # Insert before the stretch spacer at the bottom
        self.entries_layout.insertWidget(self.entries_layout.count() - 1, entry_widget)

    def _remove_entry(self, widget: CompartmentEntryWidget, *, force: bool = False):
        """Remove a compartment entry widget, ensuring at least one remains unless forced."""
        if not force and len(self.entry_widgets) == 1:
            QMessageBox.information(self, "Cannot remove", "At least one COMP entry is required.")
            return
        self.entry_widgets.remove(widget)
        widget.setParent(None)
        widget.deleteLater()

    def _clear_entries(self):
        """Remove all current compartment entries."""
        for widget in list(self.entry_widgets):
            self._remove_entry(widget, force=True)

    def get_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Collect data from all entry widgets for the 'COMP' group."""
        return {"COMP": [entry.get_values() for entry in self.entry_widgets]}

    def set_data(self, data: Dict[str, Any]):
        """Populate the tab with data from a loaded namelist."""
        comps = data.get("COMP", [])
        # Handle both single dict and list of dicts from f90nml
        if isinstance(comps, dict):
            comps = [comps]
        
        # If no entries found, start with one empty entry
        if not comps:
            comps = [{}]
            
        self._clear_entries()
        for entry in comps:
            self._add_entry(preset=entry)
