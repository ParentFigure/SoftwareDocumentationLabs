from __future__ import annotations

from business.mvc_interfaces import IUserService
from data_access.interfaces import IBankingRepository


class UserService(IUserService):
    def __init__(self, repository: IBankingRepository) -> None:
        self._repository = repository

    def get_all_users(self) -> list[dict]:
        return self._repository.list_users()

    def get_user_details(self, user_id: str) -> dict | None:
        return self._repository.get_user_details(user_id)

    def create_user(self, data: dict) -> None:
        self._validate(data)
        try:
            self._repository.create_user(
                customer_no=data["customer_no"].strip(),
                full_name=data["full_name"].strip(),
                phone=data["phone"].strip(),
                email=data["email"].strip(),
                password_hash=data["password_hash"].strip(),
            )
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def update_user(self, user_id: str, data: dict) -> None:
        self._validate(data)
        try:
            self._repository.update_user(
                user_id=user_id,
                customer_no=data["customer_no"].strip(),
                full_name=data["full_name"].strip(),
                phone=data["phone"].strip(),
                email=data["email"].strip(),
                password_hash=data["password_hash"].strip(),
            )
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def delete_user(self, user_id: str) -> None:
        try:
            self._repository.delete_user(user_id)
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

    def _validate(self, data: dict) -> None:
        if not data.get("customer_no", "").strip():
            raise ValueError("Номер клієнта не може бути порожнім")
        if not data.get("full_name", "").strip():
            raise ValueError("ПІБ клієнта не може бути порожнім")
        if not data.get("phone", "").strip():
            raise ValueError("Телефон не може бути порожнім")
        if not data.get("email", "").strip():
            raise ValueError("Email не може бути порожнім")
        if not data.get("password_hash", "").strip():
            raise ValueError("Пароль/хеш не може бути порожнім")
