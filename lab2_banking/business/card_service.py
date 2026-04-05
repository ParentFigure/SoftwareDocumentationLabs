from __future__ import annotations

from business.mvc_interfaces import ICardService
from data_access.interfaces import IBankingRepository


class CardService(ICardService):
    def __init__(self, repository: IBankingRepository) -> None:
        self._repository = repository

    def get_all_cards(self) -> list[dict]:
        return self._repository.list_cards()

    def get_card_details(self, card_id: str) -> dict | None:
        return self._repository.get_card_details(card_id)

    def create_card(self, data: dict) -> None:
        self._validate(data)
        try:
            self._repository.create_card(
                account_id=data["account_id"].strip(),
                masked_pan=data["masked_pan"].strip(),
                status=data["status"].strip().upper(),
            )
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def update_card(self, card_id: str, data: dict) -> None:
        self._validate(data)
        try:
            self._repository.update_card(
                card_id=card_id,
                account_id=data["account_id"].strip(),
                masked_pan=data["masked_pan"].strip(),
                status=data["status"].strip().upper(),
            )
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def delete_card(self, card_id: str) -> None:
        try:
            self._repository.delete_card(card_id)
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def get_account_choices(self) -> list[dict]:
        return self._repository.list_account_choices()

    def _validate(self, data: dict) -> None:
        if not data.get("account_id", "").strip():
            raise ValueError("Потрібно вибрати рахунок")
        if not data.get("masked_pan", "").strip():
            raise ValueError("Номер картки не може бути порожнім")
        if not data.get("status", "").strip():
            raise ValueError("Вкажіть статус картки")
