import sys
import os
import f90nml
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QTextEdit, QPushButton, 
                             QMenuBar, QMenu, QFileDialog, QLabel, QLineEdit,
                             QScrollArea, QFormLayout, QGroupBox)
from PySide6.QtGui import QAction
from namelist_definitions import NAMELISTS
from General import General
from Thermal_Properties import Thermal_Properties

# --- Shared Tab Base Class ---
class NamelistTab(QWidget):
    def __init__(self, parent=None, groups=None, multi=False):
        super().__init__(parent)
        self.groups = groups or []
        self.multi = multi
        self.layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.form_layout = QVBoxLayout(self.container)
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)
        
        self.fields = {} # Stores QLineEdit/Widgets by (group, var_name)
        
        for group in self.groups:
            box = QGroupBox(f"&{group}")
            flay = QFormLayout()
            # This is a simplified field generation. 
            # In a full implementation, we'd parse namelist_inputs.f90 for defaults.
            # Here we provide a few example fields based on the requirement.
            self.add_group_fields(group, flay)
            box.setLayout(flay)
            self.form_layout.addWidget(box)
            
    def add_group_fields(self, group, layout):
        # Placeholder for dynamic field generation based on namelist_inputs.f90
        # For brevity, we add a generic field for the group
        le = QLineEdit()
        layout.addRow(f"{group} Parameters:", le)
        self.fields[group] = le

    def get_data(self):
        data = {}
        for group, widget in self.fields.items():
            data[group] = widget.text()
        return data

    def set_data(self, data):
        for group, val in data.items():
            if group in self.fields:
                self.fields[group].setText(str(val))

# --- Specific Tab Implementations ---

#class General(NamelistTab):
#    def __init__(self, parent=None):
#        super().__init__(parent, groups=['HEAD', 'TIME', 'INIT', 'MISC'], multi=False)

#class Thermal_Properties(NamelistTab):
#    def __init__(self, parent=None):
#        super().__init__(parent, groups=['MATL'], multi=True)

class Compartments(NamelistTab):
    def __init__(self, parent=None):
        super().__init__(parent, groups=['COMP'], multi=True)

class Wall_Vents(NamelistTab):
    def __init__(self, parent=None):
        super().__init__(parent, groups=['VENT'], multi=True)

class Ceiling_Vents(NamelistTab):
    def __init__(self, parent=None):
        super().__init__(parent, groups=['VENT'], multi=True)

class Mechanical_Vents(NamelistTab):
    def __init__(self, parent=None):
        super().__init__(parent, groups=['VENT'], multi=True)

class Fires(NamelistTab):
    def __init__(self, parent=None):
        super().__init__(parent, groups=['FIRE', 'CHEM'], multi=True)

class Targets(NamelistTab):
    def __init__(self, parent=None):
        super().__init__(parent, groups=['DEVC'], multi=True)

class Detection_and_Suppression(NamelistTab):
    def __init__(self, parent=None):
        super().__init__(parent, groups=['DEVC'], multi=True)

class Surface_Connections(NamelistTab):
    def __init__(self, parent=None):
        super().__init__(parent, groups=['CONN'], multi=True)

class Output(NamelistTab):
    def __init__(self, parent=None):
        super().__init__(parent, groups=['DUMP', 'ISOF', 'SLCF', 'DIAG', 'RAMP', 'TABL'], multi=False)

# --- Main Application Window ---

class HomePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CFAST GUI")
        self.resize(1000, 700)
        
        self.current_file = None
        self.init_ui()
        
    def init_ui(self):
        # Menubar
        self.create_menus()
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tab_list = [
            ("General", General),
            ("Thermal Properties", Thermal_Properties),
            ("Compartments", Compartments),
            ("Wall Vents", Wall_Vents),
            ("Ceiling Vents", Ceiling_Vents),
            ("Mechanical Vents", Mechanical_Vents),
            ("Fires", Fires),
            ("Targets", Targets),
            ("Detection and Suppression", Detection_and_Suppression),
            ("Surface Connections", Surface_Connections),
            ("Output", Output)
        ]
        
        self.tab_widgets = {}
        for name, cls in self.tab_list:
            widget = cls()
            self.tabs.addTab(widget, name)
            self.tab_widgets[name] = widget
            
        main_layout.addWidget(self.tabs)
        
        # Message Window
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        self.log_window.setPlaceholderText("Operation messages will appear here...")
        main_layout.addWidget(self.log_window)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        self.btn_check = QPushButton("Check Geometry")
        self.btn_run = QPushButton("Run")
        self.btn_view = QPushButton("View Output")
        
        btn_layout.addWidget(self.btn_check)
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_view)
        main_layout.addLayout(btn_layout)

    def create_menus(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        new_act = QAction("New", self)
        new_act.triggered.connect(self.file_new)
        file_menu.addAction(new_act)
        
        open_act = QAction("Open", self)
        open_act.triggered.connect(self.file_open)
        file_menu.addAction(open_act)
        
        save_act = QAction("Save", self)
        save_act.triggered.connect(self.file_save)
        file_menu.addAction(save_act)
        
        save_as_act = QAction("Save As", self)
        save_as_act.triggered.connect(self.file_save_as)
        file_menu.addAction(save_as_act)
        
        file_menu.addSeparator()
        
        # List .in files in CWD
        in_files = [f for f in os.listdir('.') if f.endswith('.in')]
        if in_files:
            for f in in_files:
                act = QAction(f, self)
                act.triggered.connect(lambda checked=False, name=f: self.load_file(name))
                file_menu.addAction(act)
            file_menu.addSeparator()

        exit_act = QAction("Exit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        
        # View Menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Select Engineering Units")
        view_menu.addAction("View CFAST Input File")
        view_menu.addAction("View CFAST Output File")
        view_menu.addAction("View CFAST Log File")
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Documentation")
        help_menu.addAction("About CFAST")

    def log(self, message):
        self.log_window.append(message)

    def file_new(self):
        self.current_file = None
        self.log("Created new input configuration.")

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Namelist File", "", "Input Files (*.in);;All Files (*)")
        if path:
            self.load_file(path)

    def load_file(self, path):
        try:
            nml = f90nml.read(path)
            self.current_file = path
            # Distribute data to tabs
            for name, widget in self.tab_widgets.items():
                widget.set_data(nml)
            self.log(f"Loaded file: {path}")
        except Exception as e:
            self.log(f"Error loading file: {str(e)}")

    def file_save(self):
        if self.current_file:
            self.save_to_path(self.current_file)
        else:
            self.file_save_as()

    def file_save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Namelist File", "", "Input Files (*.in);;All Files (*)")
        if path:
            self.save_to_path(path)

    def save_to_path(self, path):
        try:
            all_data = {}
            for name, widget in self.tab_widgets.items():
                all_data.update(widget.get_data())
            
            # Convert dict to f90nml object and write
            nml = f90nml.Namelist(all_data)
            nml.write(path, force=True)
            self.current_file = path
            self.log(f"Saved file: {path}")
        except Exception as e:
            self.log(f"Error saving file: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())
