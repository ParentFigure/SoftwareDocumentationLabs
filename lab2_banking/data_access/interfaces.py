from __future__ import annotations

from abc import ABC, abstractmethod


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
    @abstractmethod
    def list_users(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_user_details(self, user_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def create_user(
        self,
        customer_no: str,
        full_name: str,
        phone: str,
        email: str,
        password_hash: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def update_user(
        self,
        user_id: str,
        customer_no: str,
        full_name: str,
        phone: str,
        email: str,
        password_hash: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        raise NotImplementedError

    def list_accounts(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_account_details(self, account_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def create_account(self, customer_no: str, iban: str, currency: str, balance: float):
        raise NotImplementedError

    @abstractmethod
    def update_account(self, account_id: str, iban: str, currency: str, balance: float):
        raise NotImplementedError

    @abstractmethod
    def delete_account(self, account_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_customers(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def list_account_choices(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def list_cards(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_card_details(self, card_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def create_card(self, account_id: str, masked_pan: str, status: str):
        raise NotImplementedError

    @abstractmethod
    def update_card(self, card_id: str, account_id: str, masked_pan: str, status: str):
        raise NotImplementedError

    @abstractmethod
    def delete_card(self, card_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_transactions(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_transaction_details(self, tx_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def create_transaction(
        self,
        account_id: str,
        tx_type: str,
        amount: float,
        status: str,
        created_at: str | None = None,
        target_iban: str | None = None,
        bill_id: str | None = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def update_transaction(
        self,
        tx_id: str,
        account_id: str,
        tx_type: str,
        amount: float,
        status: str,
        created_at: str | None = None,
        target_iban: str | None = None,
        bill_id: str | None = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def delete_transaction(self, tx_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
