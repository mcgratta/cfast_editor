from typing import Any, Dict
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QVBoxLayout

class NamelistTabBase(QWidget):
    def __init__(self, group_names, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_names = group_names
        self.fields: Dict[str, Dict[str, QLineEdit]] = {}
        layout = QVBoxLayout(self)
        self.form = QFormLayout()
        layout.addLayout(self.form)
        # each subclass adds actual widgets

    def register_field(self, group: str, var_name: str, widget: QLineEdit):
        self.fields.setdefault(group, {})[var_name] = widget

    def get_data(self) -> Dict[str, Dict[str, Any]]:
        data: Dict[str, Dict[str, Any]] = {}
        for group, vars_dict in self.fields.items():
            data[group] = {}
            for var_name, widget in vars_dict.items():
                value = widget.text().strip()
                data[group][var_name] = value
        return data

    def set_data(self, namelist_dict: Dict[str, Dict[str, Any]]):
        for group, vars_dict in namelist_dict.items():
            if group not in self.fields:
                continue
            for var_name, value in vars_dict.items():
                widget = self.fields[group].get(var_name)
                if widget is not None:
                    widget.setText(str(value))
