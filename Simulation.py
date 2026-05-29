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
from Compartments import Compartments
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
                elif name == "Compartments":
                    self.compartments = Compartments(thermal_properties_tab=self.thermal_properties)
                    layout.addWidget(self.compartments)
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

        if hasattr(self, "compartments"):
            comp_entries = self.compartments.get_data()
            
        for entry in comp_entries:
            formatted = self._format_comp_entry(entry)
            if not formatted:
                continue
            sections.append("&COMP")
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

    def _format_comp_entry(self, entry: dict) -> dict:
        """Format a compartment dictionary into the ordered COMP namelist fields."""
        def quote_string(value):
            text = str(value).strip()
            if not text:
                return None
            if (text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')):
                return text
            return f"'{text}'"

        def format_array(values, quote=False):
            if not values:
                return None
            cleaned = []
            for val in values:
                if val is None:
                    continue
                text = str(val).strip()
                if not text:
                    continue
                if quote:
                    quoted = quote_string(text)
                    if quoted:
                        cleaned.append(quoted)
                else:
                    cleaned.append(text)
            if not cleaned:
                return None
            return f"({', '.join(cleaned)})"

        def set_field(key, value):
            if value not in (None, "", []):
                formatted[key] = value

        formatted = {}

        set_field("cross_sect_areas", format_array(entry.get("cross_sect_areas")))
        set_field("cross_sect_heights", format_array(entry.get("cross_sect_heights")))
        set_field("depth", entry.get("depth"))
        set_field("grid", entry.get("grid"))
        set_field("hall", entry.get("hall"))
        set_field("height", entry.get("height"))
        set_field("id", quote_string(entry.get("id")) or quote_string(entry.get("comp_id")))
        set_field("fyi", quote_string(entry.get("fyi")))
        set_field("ceiling_matl_id", format_array(entry.get("ceiling_matl_id"), quote=True))
        set_field("floor_matl_id", format_array(entry.get("floor_matl_id"), quote=True))
        set_field("wall_matl_id", format_array(entry.get("wall_matl_id"), quote=True))
        set_field("ceiling_thickness", format_array(entry.get("ceiling_thickness")))
        set_field("floor_thickness", format_array(entry.get("floor_thickness")))
        set_field("wall_thickness", format_array(entry.get("wall_thickness")))
        set_field("origin", format_array(entry.get("origin")))
        set_field("shaft", entry.get("shaft"))
        set_field("width", entry.get("width"))
        set_field("leak_area_ratio", format_array(entry.get("leak_area_ratio")))
        set_field("leak_area", format_array(entry.get("leak_area")))
        set_field("flow_coefficient", entry.get("flow_coefficient"))

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
        cleaned = self._collapse_continuations(self._strip_comments(text))
        sections = self._tokenize_sections(cleaned)

        parsed = {}
        matl_entries = []
        for name, blocks in sections.items():
            if name == "MATL":
                matl_entries.extend(blocks)
            else:
                for block in blocks:
                    parsed.update(block)
        return parsed, matl_entries

    def _strip_comments(self, text):
        result = []
        in_quote = False
        quote_char = ""
        i = 0
        while i < len(text):
            ch = text[i]
            if ch in "\"'":
                result.append(ch)
                if not in_quote:
                    in_quote = True
                    quote_char = ch
                elif ch == quote_char:
                    if i + 1 < len(text) and text[i + 1] == quote_char:
                        result.append(text[i + 1])
                        i += 1
                    else:
                        in_quote = False
                        quote_char = ""
                i += 1
            elif ch == "!" and not in_quote:
                while i < len(text) and text[i] not in "\n\r":
                    i += 1
            else:
                result.append(ch)
                i += 1
        return "".join(result)

    def _collapse_continuations(self, text):
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        result = []
        i = 0
        while i < len(normalized):
            if normalized[i] == "&":
                j = i + 1
                while j < len(normalized) and normalized[j] in " \t":
                    j += 1
                if j < len(normalized) and normalized[j] == "\n":
                    result.append(" ")
                    i = j + 1
                    continue
            result.append(normalized[i])
            i += 1
        return "".join(result)

    def _tokenize_sections(self, text):
        sections = {}
        i = 0
        while i < len(text):
            if text[i] == "&":
                i += 1
                while i < len(text) and text[i].isspace():
                    i += 1
                start = i
                while i < len(text) and (text[i].isalnum() or text[i] == "_"):
                    i += 1
                section_name = text[start:i].upper()
                block_chars = []
                in_quote = False
                quote_char = ""
                while i < len(text):
                    ch = text[i]
                    if ch in "\"'":
                        block_chars.append(ch)
                        if not in_quote:
                            in_quote = True
                            quote_char = ch
                        elif ch == quote_char:
                            if i + 1 < len(text) and text[i + 1] == quote_char:
                                block_chars.append(text[i + 1])
                                i += 1
                            else:
                                in_quote = False
                                quote_char = ""
                        i += 1
                        continue
                    if ch == "/" and not in_quote:
                        i += 1
                        break
                    block_chars.append(ch)
                    i += 1
                block_text = "".join(block_chars)
                block_data = self._parse_assignments(block_text)
                if block_data:
                    sections.setdefault(section_name, []).append(block_data)
            else:
                i += 1
        return sections

    def _parse_assignments(self, block):
        data = {}
        idx = 0
        length = len(block)
        while idx < length:
            # Skip leading delimiters (spaces, tabs, newlines, commas)
            while idx < length and block[idx] in " \t\r\n,":
                idx += 1
            if idx >= length:
                break

            # Parse key
            if not (block[idx].isalpha() or block[idx] == "_"):
                idx += 1
                continue
            start = idx
            while idx < length and (block[idx].isalnum() or block[idx] == "_"):
                idx += 1
            key = block[start:idx].lower()

            # Skip whitespace before '='
            while idx < length and block[idx].isspace():
                idx += 1
            if idx >= length or block[idx] != "=":
                continue
            idx += 1

            # Parse value
            value, idx = self._parse_value(block, idx)
            if value is not None:
                data[key] = value

            # After a value, skip trailing delimiters before next key
            while idx < length and block[idx] in " \t\r\n,":
                idx += 1
        return data

    def _parse_value(self, text, idx):
        while idx < len(text) and text[idx].isspace():
            idx += 1
        if idx >= len(text):
            return None, idx
        ch = text[idx]
        if ch == "(":
            idx += 1
            items = []
            current = []
            in_quote = False
            quote_char = ""
            while idx < len(text):
                ch = text[idx]
                if in_quote:
                    current.append(ch)
                    if ch == quote_char:
                        if idx + 1 < len(text) and text[idx + 1] == quote_char:
                            current.append(text[idx + 1])
                            idx += 1
                        else:
                            in_quote = False
                            quote_char = ""
                    idx += 1
                    continue
                if ch in "\"'":
                    in_quote = True
                    quote_char = ch
                    current.append(ch)
                    idx += 1
                    continue
                if ch == ",":
                    items.append("".join(current).strip())
                    current = []
                    idx += 1
                    continue
                if ch == ")":
                    items.append("".join(current).strip())
                    idx += 1
                    break
                current.append(ch)
                idx += 1
            cleaned = [item for item in items if item]
            return cleaned if cleaned else None, idx
        if ch in "\"'":
            quote = ch
            start = idx + 1
            idx += 1
            while idx < len(text):
                current = text[idx]
                if current == quote:
                    if idx + 1 < len(text) and text[idx + 1] == quote:
                        idx += 2
                        continue
                    break
                idx += 1
            value = text[start:idx]
            idx += 1
            return value, idx
        start = idx
        while idx < len(text) and text[idx] not in ",/\n\r" and not text[idx].isspace():
            idx += 1
        return text[start:idx].strip(), idx

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
