"""Save/load controller (mirrors C# SaveLoadController)."""

import json
from typing import List, Optional

from app.config import BoolData, DefaultValueModels, SaveLoadModel


class SaveLoadController:
    def __init__(self, default_value_models: DefaultValueModels) -> None:
        self._save_load_data: Optional[SaveLoadModel] = (
            default_value_models.save_load_model
        )
        self._data_list: List[BoolData] = default_value_models.bool_datas

    def do_work(self) -> str:
        _active = [e.value for e in self._data_list if e.value]

        json_str = json.dumps(self._save_load_data.__dict__, default=str)
        print(f"JSON:{json_str}")
        return json_str