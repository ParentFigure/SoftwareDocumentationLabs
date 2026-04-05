from __future__ import annotations

from abc import ABC, abstractmethod


class IAccountService(ABC):
    @abstractmethod
    def get_all_accounts(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_account_details(self, account_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def create_account(self, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_account(self, account_id: str, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_account(self, account_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_customer_choices(self) -> list[dict]:
        raise NotImplementedError


class ICardService(ABC):
    @abstractmethod
    def get_all_cards(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_card_details(self, card_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def create_card(self, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_card(self, card_id: str, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_card(self, card_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_account_choices(self) -> list[dict]:
        raise NotImplementedError


class ITransactionService(ABC):
    @abstractmethod
    def get_all_transactions(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_transaction_details(self, tx_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def create_transaction(self, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_transaction(self, tx_id: str, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_transaction(self, tx_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_account_choices(self) -> list[dict]:
        raise NotImplementedError


class IUserService(ABC):
    @abstractmethod
    def get_all_users(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_user_details(self, user_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def create_user(self, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_user(self, user_id: str, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        raise NotImplementedError
