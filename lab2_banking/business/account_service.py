from __future__ import annotations

from business.mvc_interfaces import IAccountService
from data_access.interfaces import IBankingRepository


class AccountService(IAccountService):
    def __init__(self, repository: IBankingRepository) -> None:
        self._repository = repository

    def get_all_accounts(self) -> list[dict]:
        return self._repository.list_accounts()

    def get_account_details(self, account_id: str) -> dict | None:
        return self._repository.get_account_details(account_id)

    def create_account(self, data: dict) -> None:
        self._validate(data)
        try:
            self._repository.create_account(
                customer_no=data["customer_no"].strip(),
                iban=data["iban"].strip(),
                currency=data["currency"].strip().upper(),
                balance=float(data["balance"]),
            )
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def update_account(self, account_id: str, data: dict) -> None:
        self._validate(data)
        try:
            self._repository.update_account(
                account_id=account_id,
                iban=data["iban"].strip(),
                currency=data["currency"].strip().upper(),
                balance=float(data["balance"]),
            )
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def delete_account(self, account_id: str) -> None:
        try:
            self._repository.delete_account(account_id)
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def get_customer_choices(self) -> list[dict]:
        return self._repository.list_customers()

    def _validate(self, data: dict) -> None:
        if not data.get("customer_no", "").strip():
            raise ValueError("Потрібно вибрати клієнта")
        if not data.get("iban", "").strip():
            raise ValueError("IBAN не може бути порожнім")
        if not data.get("currency", "").strip():
            raise ValueError("Вкажіть валюту рахунку")
        try:
            float(data.get("balance", 0))
        except ValueError as exc:
            raise ValueError("Баланс має бути числом") from exc
