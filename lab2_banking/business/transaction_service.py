from __future__ import annotations

from business.mvc_interfaces import ITransactionService
from data_access.interfaces import IBankingRepository


class TransactionService(ITransactionService):
    def __init__(self, repository: IBankingRepository) -> None:
        self._repository = repository

    def get_all_transactions(self) -> list[dict]:
        return self._repository.list_transactions()

    def get_transaction_details(self, tx_id: str) -> dict | None:
        return self._repository.get_transaction_details(tx_id)

    def create_transaction(self, data: dict) -> None:
        self._validate(data)
        try:
            self._repository.create_transaction(
                account_id=data["account_id"].strip(),
                tx_type=data["tx_type"].strip().upper(),
                amount=float(data["amount"]),
                status=data["status"].strip().upper(),
                created_at=data.get("created_at", "").strip() or None,
                target_iban=data.get("target_iban", "").strip() or None,
                bill_id=data.get("bill_id", "").strip() or None,
            )
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def update_transaction(self, tx_id: str, data: dict) -> None:
        self._validate(data)
        try:
            self._repository.update_transaction(
                tx_id=tx_id,
                account_id=data["account_id"].strip(),
                tx_type=data["tx_type"].strip().upper(),
                amount=float(data["amount"]),
                status=data["status"].strip().upper(),
                created_at=data.get("created_at", "").strip() or None,
                target_iban=data.get("target_iban", "").strip() or None,
                bill_id=data.get("bill_id", "").strip() or None,
            )
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def delete_transaction(self, tx_id: str) -> None:
        try:
            self._repository.delete_transaction(tx_id)
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def get_account_choices(self) -> list[dict]:
        return self._repository.list_account_choices()

    def _validate(self, data: dict) -> None:
        if not data.get("account_id", "").strip():
            raise ValueError("Потрібно вибрати рахунок")
        if not data.get("tx_type", "").strip():
            raise ValueError("Потрібно вибрати тип транзакції")
        if not data.get("status", "").strip():
            raise ValueError("Потрібно вибрати статус транзакції")
        try:
            float(data.get("amount", 0))
        except ValueError as exc:
            raise ValueError("Сума має бути числом") from exc
        tx_type = data.get("tx_type", "").strip().upper()
        if tx_type == "TRANSFER" and not data.get("target_iban", "").strip():
            raise ValueError("Для переказу потрібен IBAN отримувача")
        if tx_type == "BILL_PAYMENT" and not data.get("bill_id", "").strip():
            raise ValueError("Для оплати рахунку потрібен bill_id")
