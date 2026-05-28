from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QGridLayout,
)
from Thermal_Properties import ThermalProperties
import sys


class NamelistGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CFAST File Editor")
        self.resize(1150, 750)

        self.defaults = {
            "title": "",
            "simulation": "900.0",
            "spreadsheet": "15.0",
            "smokeview": "15.0",
            "interior_temperature": "20.0",
            "exterior_temperature": "20.0",
            "pressure": "101325.0",
            "relative_humidity": "50.0",
        }
        self.baseline_values = self.defaults.copy()

        self.tab_widget = QTabWidget()
        self.tab_frames = {}
        tabs = [
            "Simulation",
            "Thermal Properties",
            "Compartments",
            "Wall Vents",
            "Ceiling/Floor Vents",
            "Mechanical Ventilation",
            "Fires",
            "Targets",
            "Detection/Suppression",
            "Surface Connections",
            "Output",
        ]

        for name in tabs:
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            if name != "Simulation":
                if name == "Thermal Properties":
                    thermal_tab = ThermalProperties()
                    layout.addWidget(thermal_tab)
                    self.thermal_properties = thermal_tab
                else:
                    layout.addStretch()
                    layout.addWidget(QLabel(f"Placeholder for {name} configuration."))
                    layout.addStretch()
            self.tab_widget.addTab(page, name)
            self.tab_frames[name] = page

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        self.setup_simulation_tab(self.tab_frames["Simulation"])
        self.setLayout(main_layout)

    def setup_simulation_tab(self, parent: QWidget):
        layout = parent.layout()
        # clear any placeholder widgets
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.addWidget(QLabel("Title"))
        self.title_entry = QLineEdit()
        title_layout.addWidget(self.title_entry)
        layout.addLayout(title_layout)

        params_layout = QHBoxLayout()
        params_layout.setSpacing(15)

        left_grid = QGridLayout()
        left_grid.setContentsMargins(0, 0, 0, 0)
        left_grid.setVerticalSpacing(8)
        left_grid.addWidget(QLabel("Simulation Time"), 0, 0)
        self.sim_time_entry = QLineEdit()
        left_grid.addWidget(self.sim_time_entry, 0, 1)

        left_grid.addWidget(QLabel("Text Output Interval"), 1, 0)
        self.text_out_entry = QLineEdit()
        left_grid.addWidget(self.text_out_entry, 1, 1)

        left_grid.addWidget(QLabel("Smokeview Output Interval"), 2, 0)
        self.smv_out_entry = QLineEdit()
        left_grid.addWidget(self.smv_out_entry, 2, 1)

        params_layout.addLayout(left_grid)

        right_grid = QGridLayout()
        right_grid.setContentsMargins(0, 0, 0, 0)
        right_grid.setVerticalSpacing(8)
        right_grid.addWidget(QLabel("Interior Temperature (\u00b0C)"), 0, 0)
        self.int_temp_entry = QLineEdit()
        right_grid.addWidget(self.int_temp_entry, 0, 1)

        right_grid.addWidget(QLabel("Exterior Temperature (\u00b0C)"), 1, 0)
        self.ext_temp_entry = QLineEdit()
        right_grid.addWidget(self.ext_temp_entry, 1, 1)

        right_grid.addWidget(QLabel("Pressure (Pa)"), 2, 0)
        self.pressure_entry = QLineEdit()
        right_grid.addWidget(self.pressure_entry, 2, 1)

        right_grid.addWidget(QLabel("Humidity (%)"), 3, 0)
        self.humidity_entry = QLineEdit()
        right_grid.addWidget(self.humidity_entry, 3, 1)

        params_layout.addLayout(right_grid)
        layout.addLayout(params_layout)

        self.entry_widgets = {
            "title": self.title_entry,
            "simulation": self.sim_time_entry,
            "spreadsheet": self.text_out_entry,
            "smokeview": self.smv_out_entry,
            "interior_temperature": self.int_temp_entry,
            "exterior_temperature": self.ext_temp_entry,
            "pressure": self.pressure_entry,
            "relative_humidity": self.humidity_entry,
        }

        self._apply_values(self.defaults)
        self.baseline_values = self.defaults.copy()

        layout.addWidget(QLabel("Information/Errors:"))
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text, stretch=1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.open_file_dialog)
        buttons_layout.addWidget(self.open_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_namelist)
        buttons_layout.addWidget(self.save_btn)

        self.check_geo_btn = QPushButton("Check Geometry")
        buttons_layout.addWidget(self.check_geo_btn)

        self.run_btn = QPushButton("Run")
        buttons_layout.addWidget(self.run_btn)

        self.view_btn = QPushButton("View")
        buttons_layout.addWidget(self.view_btn)

        layout.addLayout(buttons_layout)

    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open input file",
            ".",
            "Input Files (*.in);;All Files (*)",
        )
        if not filename:
            return

        try:
            with open(filename, "r") as file:
                content = file.read()
        except OSError as exc:
            self.log_info(f"Failed to open {filename}: {exc}")
            return

        parsed, matl_entries = self._parse_namelist_content(content)
        updated = {**self.defaults, **parsed}
        self._apply_values(updated)
        if hasattr(self, "thermal_properties") and matl_entries:
            self.thermal_properties.set_data(matl_entries)
        self.baseline_values = updated.copy()
        self.log_info(f"Loaded parameters from {filename}")

    def save_namelist(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save namelist input file",
            "",
            "Input Files (*.in);;All Files (*)",
        )
        if not filepath:
            return

        content = self._generate_namelist()
        if not content:
            self.log_info("No parameters were changed; nothing to save.")
            return

        try:
            with open(filepath, "w") as file:
                file.write(content)
            self.baseline_values = self._gather_current_values()
            self.log_info(f"Namelist saved to {filepath}")
        except OSError as exc:
            self.log_info(f"Failed to save file: {exc}")

    def _generate_namelist(self):
        sections = []

        head_lines = []
        value = self._get_current_value("title")
        head_lines.append(f"title = '{value}'")

        time_lines = []
        for key in ("simulation", "spreadsheet", "smokeview"):
            time_lines.append(f"{key} = {self._get_current_value(key)}")

        init_lines = []
        for key in ("interior_temperature", "exterior_temperature", "pressure", "relative_humidity"):
            init_lines.append(f"{key} = {self._get_current_value(key)}")

        if head_lines:
            sections.append("&HEAD")
            sections.extend(f" {line}" for line in head_lines)
            sections.append("/")
            sections.append("")

        if time_lines:
            sections.append("&TIME")
            sections.extend(f" {line}" for line in time_lines)
            sections.append("/")
            sections.append("")

        if init_lines:
            sections.append("&INIT")
            sections.extend(f" {line}" for line in init_lines)
            sections.append("/")
            sections.append("")

        matl_entries = []
        if hasattr(self, "thermal_properties"):
            matl_entries = self.thermal_properties.get_data()

        for entry in matl_entries:
            formatted = self._format_matl_entry(entry)
            if not formatted:
                continue
            sections.append("&MATL")
            sections.extend(f" {key} = {value}" for key, value in formatted.items())
            sections.append("/")
            sections.append("")

        return "\n".join(sections)

    def _format_matl_entry(self, entry: dict) -> dict:
        """Keep the MATL fields in the correct order and quote strings."""
        ordered_keys = [
            "material",
            "id",
            "density",
            "conductivity",
            "specific_heat",
            "emissivity",
            "thickness",
        ]
        formatted = {}
        for key in ordered_keys:
            value = entry.get(key)
            if value in (None, ""):
                continue
            if key in {"material", "id"}:
                formatted[key] = f"'{value}'"
            else:
                formatted[key] = value
        return formatted

    def _apply_values(self, values):
        for key, widget in self.entry_widgets.items():
            widget.setText(values.get(key, ""))

    def _has_field_changed(self, key):
        current = self.entry_widgets[key].text().strip()
        if not current:
            return False
        baseline = self.baseline_values.get(key, self.defaults.get(key, ""))
        return current != baseline

    def _get_current_value(self, key):
        current = self.entry_widgets[key].text().strip()
        if current:
            return current
        return self.baseline_values.get(key, self.defaults.get(key, ""))

    def _gather_current_values(self):
        return {key: self._get_current_value(key) for key in self.entry_widgets}

    def _parse_namelist_content(self, text):
        parsed = {}
        matl_entries = []
        current_section = None
        current_block = {}

        def flush_block():
            nonlocal current_section, current_block
            if current_section == "MATL" and current_block:
                matl_entries.append(current_block)
            current_block = {}

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("!"):
                continue
            if stripped.startswith("&"):
                flush_block()
                current_section = stripped[1:].split()[0].upper()
                continue
            if stripped == "/":
                flush_block()
                current_section = None
                continue
            if "=" in stripped:
                key, value = stripped.split("=", 1)
                key = key.strip().lower()
                value = value.split("!")[0].strip().rstrip(",")
                value = self._trim_quotes(value)
                if current_section == "MATL":
                    current_block[key] = value
                else:
                    parsed[key] = value
        flush_block()
        return parsed, matl_entries


    def _trim_quotes(self, value):
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            return value[1:-1]
        return value

    def log_info(self, message):
        self.info_text.append(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = NamelistGUI()
    gui.show()
    sys.exit(app.exec())
