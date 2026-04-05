from __future__ import annotations

from abc import ABC, abstractmethod


class IImportPresenter(ABC):
    @abstractmethod
    def show_import_result(self, stats: dict[str, int]) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_error(self, message: str) -> None:
        raise NotImplementedError
