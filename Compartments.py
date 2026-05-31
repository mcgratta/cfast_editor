from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHBoxLayout, QHeaderView, QComboBox, 
    QCheckBox, QLabel, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt

class Compartments(QWidget):
    def __init__(self, thermal_properties_tab=None):
        """
        Initialize the Compartments tab.
        :param thermal_properties_tab: Reference to the ThermalProperties class instance to fetch materials.
        """
        super().__init__()
        self.thermal_properties_tab = thermal_properties_tab
        self.layout = QVBoxLayout(self)

        # Main Table Headers for the COMP namelist
        self.headers = [
            "ID", "Width (m)", "Depth (m)", "Height (m)",
            "X Position (m)", "Y Position (m)", "Z Position (m)",
            "Wall Leak Area Ratio", "Floor Leak Area Ratio",
            "Ceiling 1", "C. Thick 1", "Ceiling 2", "C. Thick 2", "Ceiling 3", "C. Thick 3",
            "Walls 1", "W. Thick 1", "Walls 2", "W. Thick 2", "Walls 3", "W. Thick 3",
            "Floor 1", "F. Thick 1", "Floor 2", "F. Thick 2", "Floor 3", "F. Thick 3",
            "Flow Characteristics", "Variable Cross-Section?"
        ]
        
        # Mapping to COMP namelist parameters in namelist_inputs.f90
        self.namelist_map = [
            "id", "width", "depth", "height",
            "origin(1)", "origin(2)", "origin(3)",
            "leak_area(1)", "leak_area(2)",
            "ceiling_matl_id(1)", "ceiling_thickness(1)", "ceiling_matl_id(2)", "ceiling_thickness(2)", "ceiling_matl_id(3)", "ceiling_thickness(3)",
            "wall_matl_id(1)", "wall_thickness(1)", "wall_matl_id(2)", "wall_thickness(2)", "wall_matl_id(3)", "wall_thickness(3)",
            "floor_matl_id(1)", "floor_thickness(1)", "floor_matl_id(2)", "floor_thickness(2)", "floor_matl_id(3)", "floor_thickness(3)",
            "flow_char", "variable_cross"
        ]

        # Initialize Main Compartment Table
        self.table = QTableWidget(0, len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.layout.addWidget(self.table)

        # Row management buttons
        btn_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("Add Compartment")
        self.add_row_btn.clicked.connect(self.add_row)
        
        self.remove_row_btn = QPushButton("Delete Compartment")
        self.remove_row_btn.clicked.connect(self.remove_row)
        
        btn_layout.addWidget(self.add_row_btn)
        btn_layout.addWidget(self.remove_row_btn)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        # Variable Cross-Section Table (Hidden by default)
        self.cross_sect_group = QGroupBox("Variable Cross-Sectional Area")
        self.cross_sect_layout = QVBoxLayout(self.cross_sect_group)
        
        self.cross_sect_table = QTableWidget(0, 2)
        self.cross_sect_table.setHorizontalHeaderLabels(["Height (m)", "Area (m2)"])
        self.cross_sect_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cross_sect_layout.addWidget(self.cross_sect_table)
        
        cs_btn_layout = QHBoxLayout()
        self.add_cs_row_btn = QPushButton("Add Row")
        self.add_cs_row_btn.clicked.connect(self.add_cs_row)
        self.remove_cs_row_btn = QPushButton("Delete Row")
        self.remove_cs_row_btn.clicked.connect(self.remove_cs_row)
        cs_btn_layout.addWidget(self.add_cs_row_btn)
        cs_btn_layout.addWidget(self.remove_cs_row_btn)
        cs_btn_layout.addStretch()
        self.cross_sect_layout.addLayout(cs_btn_layout)
        
        self.layout.addWidget(self.cross_sect_group)
        self.cross_sect_group.setVisible(False)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # ID and Dimensions (Cols 0-8)
        for col in range(9):
            self.table.setItem(row, col, QTableWidgetItem(""))

        # Material Dropdowns and Thicknesses (Cols 9-26)
        # Layers for Ceiling, Walls, Floor
        mat_cols = [9, 11, 13, 15, 17, 19, 21, 23, 25]
        thick_cols = [10, 12, 14, 16, 18, 20, 22, 24, 26]
        
        for col in mat_cols:
            combo = QComboBox()
            self.refresh_material_combo(combo)
            self.table.setCellWidget(row, col, combo)
            
        for col in thick_cols:
            self.table.setItem(row, col, QTableWidgetItem("0.0"))

        # Flow Characteristics (Col 27)
        flow_combo = QComboBox()
        flow_combo.addItems(["Normal", "Shaft", "Corridor"])
        self.table.setCellWidget(row, 27, flow_combo)

        # Variable Cross-Section Checkbox (Col 28)
        container = QWidget()
        cb_layout = QHBoxLayout(container)
        check_box = QCheckBox()
        check_box.stateChanged.connect(self.update_cs_visibility)
        cb_layout.addWidget(check_box)
        cb_layout.setAlignment(Qt.AlignCenter)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 28, container)

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self.update_cs_visibility()

    def refresh_material_combo(self, combo):
        """Populates the dropdown with materials from the Thermal Properties tab."""
        current_selection = combo.currentText()
        combo.clear()
        combo.addItem("OFF")
        if self.thermal_properties_tab:
            materials = self.thermal_properties_tab.get_data()
            for mat in materials:
                mat_id = mat.get("id")
                if mat_id:
                    combo.addItem(mat_id)
        
        index = combo.findText(current_selection)
        if index >= 0:
            combo.setCurrentIndex(index)

    def update_cs_visibility(self):
        """Shows the Variable Cross-Section table if any checkbox is checked."""
        show = False
        for row in range(self.table.rowCount()):
            container = self.table.cellWidget(row, 28)
            if container:
                checkbox = container.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    show = True
                    break
        self.cross_sect_group.setVisible(show)

    def add_cs_row(self):
        row = self.cross_sect_table.rowCount()
        self.cross_sect_table.insertRow(row)
        self.cross_sect_table.setItem(row, 0, QTableWidgetItem("0.0"))
        self.cross_sect_table.setItem(row, 1, QTableWidgetItem("0.0"))

    def remove_cs_row(self):
        current_row = self.cross_sect_table.currentRow()
        if current_row >= 0:
            self.cross_sect_table.removeRow(current_row)

    def get_data(self):
        """Extracts data for COMP namelist generation."""
        compartments = []
        for row in range(self.table.rowCount()):
            data = {}
            # Basic params
            data["id"] = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            data["width"] = self.table.item(row, 1).text() if self.table.item(row, 1) else "0.0"
            data["depth"] = self.table.item(row, 2).text() if self.table.item(row, 2) else "0.0"
            data["height"] = self.table.item(row, 3).text() if self.table.item(row, 3) else "0.0"
            
            # Origin array
            data["origin"] = [
                self.table.item(row, 4).text() if self.table.item(row, 4) else "0.0",
                self.table.item(row, 5).text() if self.table.item(row, 5) else "0.0",
                self.table.item(row, 6).text() if self.table.item(row, 6) else "0.0"
            ]
            
            # Leak area array
            data["leak_area"] = [
                self.table.item(row, 7).text() if self.table.item(row, 7) else "0.0",
                self.table.item(row, 8).text() if self.table.item(row, 8) else "0.0"
            ]

            # Materials and Thicknesses (3 layers each)
            data["ceiling_matl_id"] = [self.table.cellWidget(row, c).currentText() for c in [9, 11, 13]]
            data["ceiling_thickness"] = [self.table.item(row, c).text() for c in [10, 12, 14]]
            
            data["wall_matl_id"] = [self.table.cellWidget(row, c).currentText() for c in [15, 17, 19]]
            data["wall_thickness"] = [self.table.item(row, c).text() for c in [16, 18, 20]]
            
            data["floor_matl_id"] = [self.table.cellWidget(row, c).currentText() for c in [21, 23, 25]]
            data["floor_thickness"] = [self.table.item(row, c).text() for c in [22, 24, 26]]

            # Flow Characteristics logic
            flow = self.table.cellWidget(row, 27).currentText()
            data["shaft"] = ".TRUE." if flow == "Shaft" else ".FALSE."
            data["hall"] = ".TRUE." if flow == "Corridor" else ".FALSE."

            # Variable Cross Section Data
            container = self.table.cellWidget(row, 28)
            if container and container.findChild(QCheckBox).isChecked():
                heights = []
                areas = []
                for cs_row in range(self.cross_sect_table.rowCount()):
                    h_item = self.cross_sect_table.item(cs_row, 0)
                    a_item = self.cross_sect_table.item(cs_row, 1)
                    if h_item and a_item:
                        heights.append(h_item.text())
                        areas.append(a_item.text())
                data["cross_sect_heights"] = heights
                data["cross_sect_areas"] = areas

            compartments.append(data)
        return compartments

    def set_data(self, comp_list):
        """Populates the table from parsed COMP namelist dictionaries."""
        self.table.setRowCount(0)
        self.cross_sect_table.setRowCount(0)
        cross_loaded = False

        for entry in comp_list:
            self.add_row()
            row = self.table.rowCount() - 1

            self._set_item_text(row, 0, self._value_to_str(entry.get("id") or entry.get("comp_id")))
            self._set_item_text(row, 1, self._value_to_str(entry.get("width"), "0.0"))
            self._set_item_text(row, 2, self._value_to_str(entry.get("depth"), "0.0"))
            self._set_item_text(row, 3, self._value_to_str(entry.get("height"), "0.0"))

            origin = self._normalize_list(entry, "origin", 3, "0.0")
            for idx, col in enumerate(range(4, 7)):
                self._set_item_text(row, col, origin[idx])

            leak_key = "leak_area" if "leak_area" in entry else ("leak_area_ratio" if "leak_area_ratio" in entry else None)
            leak = self._normalize_list(entry, leak_key, 2, "0.0") if leak_key else ["0.0", "0.0"]
            for idx, col in enumerate([7, 8]):
                self._set_item_text(row, col, leak[idx])

            ceiling_ids = self._normalize_list(entry, "ceiling_matl_id", 3, "OFF")
            ceiling_th = self._normalize_list(entry, "ceiling_thickness", 3, "0.0")
            for idx, col in enumerate([9, 11, 13]):
                self._set_combo_value(row, col, ceiling_ids[idx])
            for idx, col in enumerate([10, 12, 14]):
                self._set_item_text(row, col, ceiling_th[idx])

            wall_ids = self._normalize_list(entry, "wall_matl_id", 3, "OFF")
            wall_th = self._normalize_list(entry, "wall_thickness", 3, "0.0")
            for idx, col in enumerate([15, 17, 19]):
                self._set_combo_value(row, col, wall_ids[idx])
            for idx, col in enumerate([16, 18, 20]):
                self._set_item_text(row, col, wall_th[idx])

            floor_ids = self._normalize_list(entry, "floor_matl_id", 3, "OFF")
            floor_th = self._normalize_list(entry, "floor_thickness", 3, "0.0")
            for idx, col in enumerate([21, 23, 25]):
                self._set_combo_value(row, col, floor_ids[idx])
            for idx, col in enumerate([22, 24, 26]):
                self._set_item_text(row, col, floor_th[idx])

            flow_text = self._determine_flow(entry)
            self._set_combo_value(row, 27, flow_text)

            checkbox = self._describe_variable_cross_checkbox(row)
            cross_heights = self._normalize_list(entry, "cross_sect_heights", None)
            cross_areas = self._normalize_list(entry, "cross_sect_areas", None)
            has_cross = bool(cross_heights or cross_areas)
            if checkbox:
                checkbox.setChecked(has_cross)
            if has_cross and not cross_loaded:
                self._populate_cross_section_table(cross_heights, cross_areas)
                cross_loaded = True

        self.update_cs_visibility()

    def _set_item_text(self, row, col, text):
        item = self.table.item(row, col)
        if item is None:
            item = QTableWidgetItem()
            self.table.setItem(row, col, item)
        item.setText(text)

    def _set_combo_value(self, row, col, text):
        combo = self.table.cellWidget(row, col)
        if not combo:
            return
        cleaned = self._value_to_str(text, "OFF")
        index = combo.findText(cleaned)
        if index < 0:
            combo.addItem(cleaned)
            index = combo.count() - 1
        combo.setCurrentIndex(index)

    def _normalize_list(self, entry, key, count=None, default=""):
        if key is None:
            return [default] * count if count is not None else []
        raw = entry.get(key)
        values = []
        if isinstance(raw, list):
            values = [self._value_to_str(item, default) for item in raw]
        elif raw is not None:
            values = [self._value_to_str(raw, default)]
        if count is None:
            return values
        if len(values) < count:
            values.extend([default] * (count - len(values)))
        return values[:count]

    def _value_to_str(self, value, default=""):
        text = self._trim_quotes(value)
        if text:
            return text
        return default

    def _trim_quotes(self, value):
        if value is None:
            return ""
        text = str(value).strip()
        if len(text) >= 2 and ((text[0] == text[-1]) and text[0] in "\"'"):
            return text[1:-1]
        return text

    def _determine_flow(self, entry):
        shaft = str(entry.get("shaft", "")).strip().upper() == ".TRUE."
        hall = str(entry.get("hall", "")).strip().upper() == ".TRUE."
        if shaft:
            return "Shaft"
        if hall:
            return "Corridor"
        char = self._trim_quotes(entry.get("flow_char"))
        mapping = {"SHAFT": "Shaft", "CORRIDOR": "Corridor", "NORMAL": "Normal"}
        if char:
            return mapping.get(char.upper(), "Normal")
        return "Normal"

    def _populate_cross_section_table(self, heights, areas):
        self.cross_sect_table.setRowCount(0)
        rows = max(len(heights), len(areas)) if heights or areas else 0
        for idx in range(rows):
            self.cross_sect_table.insertRow(idx)
            height = heights[idx] if idx < len(heights) else "0.0"
            area = areas[idx] if idx < len(areas) else "0.0"
            self.cross_sect_table.setItem(idx, 0, QTableWidgetItem(height))
            self.cross_sect_table.setItem(idx, 1, QTableWidgetItem(area))

    def _describe_variable_cross_checkbox(self, row):
        container = self.table.cellWidget(row, 28)
        if not container:
            return None
        return container.findChild(QCheckBox)

