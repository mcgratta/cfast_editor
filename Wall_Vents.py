from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHBoxLayout, QHeaderView, QComboBox, 
    QLabel, QGroupBox, QLineEdit, QFormLayout
)
from PySide6.QtCore import Qt

class WallVents(QWidget):
    def __init__(self, compartments_tab=None):
        """
        Initialize the Wall Vents tab.
        :param compartments_tab: Reference to the Compartments class instance to fetch compartment IDs.
        """
        super().__init__()
        self.compartments_tab = compartments_tab
        self.layout = QVBoxLayout(self)

        # Main Table Headers for the VENT namelist
        self.headers = [
            "ID", "First Compartment", "Second Compartment",
            "Bottom (m)", "Height (m)", "Width (m)", "Offset (m)",
            "Face", "Open/Close Criterion"
        ]
        
        # Mapping to VENT namelist parameters
        self.namelist_map = [
            "id", "comp_ids(1)", "comp_ids(2)",
            "bottom", "height", "width", "offset",
            "face", "criterion"
        ]

        # Initialize Main Vent Table
        self.table = QTableWidget(0, len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self.update_detail_visibility)
        self.layout.addWidget(self.table)

        # Row management buttons
        btn_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("Add Vent")
        self.add_row_btn.clicked.connect(self.add_row)
        
        self.remove_row_btn = QPushButton("Delete Vent")
        self.remove_row_btn.clicked.connect(self.remove_row)
        
        btn_layout.addWidget(self.add_row_btn)
        btn_layout.addWidget(self.remove_row_btn)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        # Detail Groups for Criterion-specific parameters
        self.setup_detail_groups()

    def setup_detail_groups(self):
        # Time Criterion Table (Ramp-like)
        self.time_group = QGroupBox("Time Criterion Schedule")
        time_layout = QVBoxLayout(self.time_group)
        self.time_table = QTableWidget(0, 2)
        self.time_table.setHorizontalHeaderLabels(["Time", "Fraction"])
        self.time_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        time_layout.addWidget(self.time_table)
        
        t_btn_layout = QHBoxLayout()
        add_t_btn = QPushButton("Add Step")
        add_t_btn.clicked.connect(self.add_time_row)
        del_t_btn = QPushButton("Delete Step")
        del_t_btn.clicked.connect(self.remove_time_row)
        t_btn_layout.addWidget(add_t_btn)
        t_btn_layout.addWidget(del_t_btn)
        time_layout.addLayout(t_btn_layout)
        self.layout.addWidget(self.time_group)
        self.time_group.setVisible(False)

        # Activation Parameters (Temperature / Heat Flux)
        self.activation_group = QGroupBox("Activation Parameters")
        self.activation_form = QFormLayout(self.activation_group)
        
        self.setpoint_label = QLabel("Setpoint")
        self.setpoint_edit = QLineEdit()
        self.pre_fraction_edit = QLineEdit("1.0")
        self.post_fraction_edit = QLineEdit("1.0")
        
        self.activation_form.addRow(self.setpoint_label, self.setpoint_edit)
        self.activation_form.addRow("Pre-Activation Fraction:", self.pre_fraction_edit)
        self.activation_form.addRow("Post-Activation Fraction:", self.post_fraction_edit)
        
        self.layout.addWidget(self.activation_group)
        self.activation_group.setVisible(False)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # ID (Col 0)
        self.table.setItem(row, 0, QTableWidgetItem(f"Vent_{row+1}"))

        # Compartments (Cols 1-2)
        for col in [1, 2]:
            combo = QComboBox()
            combo.setEditable(True)
            self.refresh_compartment_combo(combo)
            self.table.setCellWidget(row, col, combo)

        # Dimensions (Cols 3-6)
        for col in range(3, 7):
            self.table.setItem(row, col, QTableWidgetItem("0.0"))

        # Face (Col 7)
        face_combo = QComboBox()
        face_combo.addItems(["Left", "Right", "Back", "Front"])
        self.table.setCellWidget(row, 7, face_combo)

        # Criterion (Col 8)
        crit_combo = QComboBox()
        crit_combo.addItems(["None", "Time", "Temperature", "Heat Flux"])
        crit_combo.currentTextChanged.connect(self.update_detail_visibility)
        self.table.setCellWidget(row, 8, crit_combo)

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self.update_detail_visibility()

    def refresh_compartment_combo(self, combo):
        current_selection = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("OUTSIDE")
        if self.compartments_tab:
            comp_data = self.compartments_tab.get_data()
            seen = {"OUTSIDE"}
            for comp in comp_data:
                raw_id = comp.get("id")
                if not raw_id:
                    continue
                cleaned = raw_id.strip()
                if not cleaned or cleaned.upper() == "NULL":
                    continue
                if cleaned not in seen:
                    combo.addItem(cleaned)
                    seen.add(cleaned)
        if current_selection:
            index = combo.findText(current_selection, Qt.MatchFixedString | Qt.MatchRecursive)
            if index >= 0:
                combo.setCurrentIndex(index)
            else:
                combo.addItem(current_selection)
                combo.setCurrentIndex(combo.count() - 1)
        combo.blockSignals(False)
        
    def update_detail_visibility(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            self.time_group.setVisible(False)
            self.activation_group.setVisible(False)
            return

        crit_combo = self.table.cellWidget(current_row, 8)
        criterion = crit_combo.currentText() if crit_combo else "None"

        self.time_group.setVisible(criterion == "Time")
        self.activation_group.setVisible(criterion in ["Temperature", "Heat Flux"])

        if criterion == "Temperature":
            self.setpoint_label.setText("Setpoint (C):")
        elif criterion == "Heat Flux":
            self.setpoint_label.setText("Setpoint (kW/m2):")

    def add_time_row(self):
        row = self.time_table.rowCount()
        self.time_table.insertRow(row)
        self.time_table.setItem(row, 0, QTableWidgetItem("0.0"))
        self.time_table.setItem(row, 1, QTableWidgetItem("1.0"))

    def remove_time_row(self):
        curr = self.time_table.currentRow()
        if curr >= 0:
            self.time_table.removeRow(curr)

    def get_data(self):
        vents = []
        for row in range(self.table.rowCount()):
            data = {}
            data["id"] = self.table.item(row, 0).text()
            data["comp_ids"] = [
                self.table.cellWidget(row, 1).currentText(),
                self.table.cellWidget(row, 2).currentText()
            ]
            data["bottom"] = self.table.item(row, 3).text()
            data["height"] = self.table.item(row, 4).text()
            data["width"] = self.table.item(row, 5).text()
            data["offset"] = self.table.item(row, 6).text()
            data["face"] = self.table.cellWidget(row, 7).currentText()
            
            crit = self.table.cellWidget(row, 8).currentText()
            data["criterion"] = crit if crit != "None" else "NULL"

            # Criterion specific data (Note: In a multi-row scenario, 
            # this implementation assumes the details belong to the currently selected row 
            # or would need to be stored per-row in a data structure).
            if crit == "Time":
                times, fractions = [], []
                for r in range(self.time_table.rowCount()):
                    times.append(self.time_table.item(r, 0).text())
                    fractions.append(self.time_table.item(r, 1).text())
                data["t"] = times
                data["f"] = fractions
            elif crit in ["Temperature", "Heat Flux"]:
                data["setpoint"] = self.setpoint_edit.text()
                data["pre_fraction"] = self.pre_fraction_edit.text()
                data["post_fraction"] = self.post_fraction_edit.text()

            vents.append(data)
        return vents

    def set_data(self, vent_list):
        self.table.setRowCount(0)
        for entry in vent_list:
            self.add_row()
            row = self.table.rowCount() - 1
            
            self.table.item(row, 0).setText(str(entry.get("id", "")))
            
            comp_ids = entry.get("comp_ids", ["NULL", "NULL"])
            if len(comp_ids) >= 1:
                self._set_combo_value(row, 1, comp_ids[0])
            if len(comp_ids) >= 2:
                self._set_combo_value(row, 2, comp_ids[1])
                
            self.table.item(row, 3).setText(str(entry.get("bottom", "0.0")))
            self.table.item(row, 4).setText(str(entry.get("height", "0.0")))
            self.table.item(row, 5).setText(str(entry.get("width", "0.0")))
            self.table.item(row, 6).setText(str(entry.get("offset", "0.0")))
            
            self._set_combo_value(row, 7, entry.get("face", "Front"))
            
            crit = entry.get("criterion", "None")
            if crit == "NULL": crit = "None"
            self._set_combo_value(row, 8, crit)

            # Detail data loading (simplified for single selection)
            if crit == "Time":
                self.time_table.setRowCount(0)
                ts = entry.get("t", [])
                fs = entry.get("f", [])
                for i in range(max(len(ts), len(fs))):
                    self.add_time_row()
                    self.time_table.item(i, 0).setText(str(ts[i] if i < len(ts) else "0.0"))
                    self.time_table.item(i, 1).setText(str(fs[i] if i < len(fs) else "1.0"))
            elif crit in ["Temperature", "Heat Flux"]:
                self.setpoint_edit.setText(str(entry.get("setpoint", "")))
                self.pre_fraction_edit.setText(str(entry.get("pre_fraction", "1.0")))
                self.post_fraction_edit.setText(str(entry.get("post_fraction", "1.0")))

    def _set_combo_value(self, row, col, text):
        combo = self.table.cellWidget(row, col)
        if combo:
            index = combo.findText(str(text))
            if index >= 0:
                combo.setCurrentIndex(index)
            else:
                combo.addItem(str(text))
                combo.setCurrentIndex(combo.count() - 1)

