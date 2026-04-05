from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigLoader:
    @staticmethod
    def load(config_path: str) -> dict[str, Any]:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)
