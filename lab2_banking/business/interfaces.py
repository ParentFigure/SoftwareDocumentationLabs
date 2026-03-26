from __future__ import annotations

from abc import ABC, abstractmethod


class IDataImportService(ABC):
    @abstractmethod
    def import_from_csv(self, csv_path: str) -> dict[str, int]:
        raise NotImplementedError
