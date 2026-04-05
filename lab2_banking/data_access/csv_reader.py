from __future__ import annotations

import csv
from pathlib import Path

from data_access.interfaces import ICsvReader


class CsvReader(ICsvReader):
    def read_rows(self, path: str) -> list[dict[str, str]]:
        csv_path = Path(path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        with csv_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        if not rows:
            raise ValueError("CSV file is empty.")

        return rows
