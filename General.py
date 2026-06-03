from PySide6.QtWidgets import QLineEdit
from namelist_definitions import NAMELISTS
from tab_base import NamelistTabBase

class General(NamelistTabBase):
    def __init__(self, parent=None):
        super().__init__(("HEAD", "TIME", "INIT", "MISC"), parent=parent)
        for group in self.group_names:
            for var_name, metadata in NAMELISTS[group].items():
                widget = QLineEdit(str(metadata["default"]))
                self.form.addRow(f"{group}.{var_name}", widget)
                self.register_field(group, var_name, widget)
