from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class ICsvReader(ABC):
    @abstractmethod
    def read_rows(self, path: str) -> list[dict[str, str]]:
        raise NotImplementedError


class IBankingRepository(ABC):
    @abstractmethod
    def init_db(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_or_create_customer(
        self,
        customer_no: str,
        full_name: str,
        phone: str,
        email: str,
        password_hash: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def get_or_create_account(
        self,
        customer_no: str,
        iban: str,
        currency: str,
        balance: float,
    ):
        raise NotImplementedError

    @abstractmethod
    def get_or_create_card(
        self,
        account_iban: str,
        masked_pan: str,
        status: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def add_transaction(
        self,
        account_iban: str,
        tx_type: str,
        amount: float,
        status: str,
        created_at: str,
        target_iban: str | None = None,
        bill_id: str | None = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
