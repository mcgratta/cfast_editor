from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHBoxLayout, QHeaderView
)
from PySide6.QtCore import Qt

class ThermalProperties(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Headings as specified for the MATL namelist
        self.headers = [
            "Material", "ID", "Density (kg/m\u00B3)", 
            "Conductivity (kW/m/K)", "Specific Heat (kJ/kg/K)", 
            "Emissivity", "Thickness (m)"
        ]
        
        # Mapping headers to namelist variable names in namelist_inputs.f90
        self.namelist_map = [
            "material", "id", "density", 
            "conductivity", "specific_heat", 
            "emissivity", "thickness"
        ]

        # Initialize Table
        self.table = QTableWidget(0, len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # Row management buttons
        btn_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("Add Row")
        self.add_row_btn.clicked.connect(self.add_row)
        
        self.remove_row_btn = QPushButton("Delete Row")
        self.remove_row_btn.clicked.connect(self.remove_row)
        
        btn_layout.addWidget(self.add_row_btn)
        btn_layout.addWidget(self.remove_row_btn)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

    def add_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        for col in range(len(self.headers)):
            self.table.setItem(row_count, col, QTableWidgetItem(""))

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def get_data(self):
        """Extracts table data into a list of dictionaries for namelist generation."""
        materials = []
        for row in range(self.table.rowCount()):
            mat_data = {}
            for col, key in enumerate(self.namelist_map):
                item = self.table.item(row, col)
                val = item.text().strip() if item else ""
                if val:
                    mat_data[key] = val
            if mat_data:
                materials.append(mat_data)
        return materials

    def set_data(self, materials_list):
        """Populates the table from a list of dictionaries (e.g., when loading a file)."""
        self.table.setRowCount(0)
        for entry in materials_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, key in enumerate(self.namelist_map):
                val = entry.get(key, "")
                self.table.setItem(row, col, QTableWidgetItem(str(val)))
