from typing import Any, Dict
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QVBoxLayout

def parse_namelist_value(text: str, metadata: Dict[str, Any]) -> Any:
    """Convert text input into the appropriate Python type for f90nml."""
    text = text.strip()
    if not text:
        return metadata.get("default")

    base_type = metadata["type"]
    if base_type.endswith("_array"):
        text_items = [item.strip() for item in text.split(",") if item.strip()]
        elem_type = base_type.replace("_array", "")
        converter = int if elem_type == "integer" else float if elem_type == "real" else str
        return [converter(item) for item in text_items] if text_items else metadata.get("default")
    if base_type == "integer":
        try:
            return int(text)
        except ValueError:
            return metadata.get("default")
    if base_type == "real":
        try:
            return float(text)
        except ValueError:
            return metadata.get("default")
    if base_type == "logical":
        lowered = text.lower()
        return lowered in ("t", "true", ".true.", "1")
    return text


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

    def get_data(self):
        data = {}
        # Correctly iterate through the nested dictionary
        for group, vars_dict in self.fields.items():
            for var_name, widget in vars_dict.items():
                value = widget.text().strip()
                if not value:
                    # Fallback to default if empty
                    from namelist_definitions import NAMELISTS
                    value = NAMELISTS[group][var_name]["default"]
                
                data.setdefault(group, {})[var_name] = value
        return data

    def set_data(self, namelist_dict):
        # Correctly iterate through the incoming data and match with nested fields
        for group, entries in namelist_dict.items():
            if isinstance(entries, dict) and group in self.fields:
                for var_name, value in entries.items():
                    if var_name in self.fields[group]:
                        self.fields[group][var_name].setText(str(value))
