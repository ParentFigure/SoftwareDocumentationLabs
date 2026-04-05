from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import requests


class DatasetService:
    def __init__(
        self,
        url: str,
        local_csv_path: str,
        timeout_seconds: int = 60,
        request_headers: dict[str, str] | None = None,
    ) -> None:
        self.url = url
        self.local_csv_path = Path(local_csv_path)
        self.timeout_seconds = timeout_seconds
        self.request_headers = request_headers or {}

    def download_to_file(self) -> Path:
        self.local_csv_path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(
            self.url,
            timeout=self.timeout_seconds,
            headers=self.request_headers,
        )
        response.raise_for_status()
        self.local_csv_path.write_bytes(response.content)
        return self.local_csv_path

    def read_rows(self, limit: int | None = None) -> list[dict[str, Any]]:
        if not self.local_csv_path.exists():
            raise FileNotFoundError(
                f"Local dataset file was not found: {self.local_csv_path}. Run with --download first."
            )

        rows: list[dict[str, Any]] = []
        with self.local_csv_path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for index, row in enumerate(reader):
                rows.append(row)
                if limit is not None and index + 1 >= limit:
                    break
        return rows

    @staticmethod
    def format_rows(rows: list[dict[str, Any]]) -> list[str]:
        formatted_lines: list[str] = []
        for row in rows:
            formatted_lines.append(
                " | ".join(
                    [
                        f"plate={row.get('plate', '')}",
                        f"state={row.get('state', '')}",
                        f"license_type={row.get('license_type', '')}",
                        f"summons_number={row.get('summons_number', '')}",
                        f"issue_date={row.get('issue_date', '')}",
                        f"violation_time={row.get('violation_time', '')}",
                        f"violation_county={row.get('violation_county', '')}",
                        f"fine_amount={row.get('fine_amount', '')}",
                        f"penalty_amount={row.get('penalty_amount', '')}",
                        f"amount_due={row.get('amount_due', '')}",
                    ]
                )
            )
        return formatted_lines
