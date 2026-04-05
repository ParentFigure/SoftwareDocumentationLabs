from __future__ import annotations

from flask import Blueprint, jsonify, request

from business.mvc_interfaces import IAccountService, ICardService, ITransactionService, IUserService


def create_api_blueprint(
    account_service: IAccountService,
    card_service: ICardService,
    transaction_service: ITransactionService,
    user_service: IUserService,
) -> Blueprint:
    bp = Blueprint("api", __name__, url_prefix="/api")

    @bp.get("/users")
    def get_users():
        return jsonify(user_service.get_all_users())

    @bp.get("/users/<user_id>")
    def get_user(user_id: str):
        user = user_service.get_user_details(user_id)
        return (jsonify(user), 200) if user else (jsonify({"error": "User not found"}), 404)

    @bp.post("/users")
    def post_user():
        data = request.get_json(force=True)
        try:
            user_service.create_user(data)
            return jsonify({"message": "User created"}), 201
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.put("/users/<user_id>")
    def put_user(user_id: str):
        data = request.get_json(force=True)
        try:
            user_service.update_user(user_id, data)
            return jsonify({"message": "User updated"})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.delete("/users/<user_id>")
    def delete_user(user_id: str):
        try:
            user_service.delete_user(user_id)
            return jsonify({"message": "User deleted"})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.get("/accounts")
    def get_accounts():
        return jsonify(account_service.get_all_accounts())

    @bp.get("/accounts/<account_id>")
    def get_account(account_id: str):
        account = account_service.get_account_details(account_id)
        return (jsonify(account), 200) if account else (jsonify({"error": "Account not found"}), 404)

    @bp.post("/accounts")
    def post_account():
        data = request.get_json(force=True)
        try:
            account_service.create_account(data)
            return jsonify({"message": "Account created"}), 201
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.put("/accounts/<account_id>")
    def put_account(account_id: str):
        data = request.get_json(force=True)
        try:
            account_service.update_account(account_id, data)
            return jsonify({"message": "Account updated"})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.delete("/accounts/<account_id>")
    def delete_account(account_id: str):
        try:
            account_service.delete_account(account_id)
            return jsonify({"message": "Account deleted"})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.get("/cards")
    def get_cards():
        return jsonify(card_service.get_all_cards())

    @bp.get("/cards/<card_id>")
    def get_card(card_id: str):
        card = card_service.get_card_details(card_id)
        return (jsonify(card), 200) if card else (jsonify({"error": "Card not found"}), 404)

    @bp.post("/cards")
    def post_card():
        data = request.get_json(force=True)
        try:
            card_service.create_card(data)
            return jsonify({"message": "Card created"}), 201
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.put("/cards/<card_id>")
    def put_card(card_id: str):
        data = request.get_json(force=True)
        try:
            card_service.update_card(card_id, data)
            return jsonify({"message": "Card updated"})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.delete("/cards/<card_id>")
    def delete_card(card_id: str):
        try:
            card_service.delete_card(card_id)
            return jsonify({"message": "Card deleted"})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.get("/transactions")
    def get_transactions():
        return jsonify(transaction_service.get_all_transactions())

    @bp.get("/transactions/<tx_id>")
    def get_transaction(tx_id: str):
        tx = transaction_service.get_transaction_details(tx_id)
        return (jsonify(tx), 200) if tx else (jsonify({"error": "Transaction not found"}), 404)

    @bp.post("/transactions")
    def post_transaction():
        data = request.get_json(force=True)
        try:
            transaction_service.create_transaction(data)
            return jsonify({"message": "Transaction created"}), 201
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.put("/transactions/<tx_id>")
    def put_transaction(tx_id: str):
        data = request.get_json(force=True)
        try:
            transaction_service.update_transaction(tx_id, data)
            return jsonify({"message": "Transaction updated"})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.delete("/transactions/<tx_id>")
    def delete_transaction(tx_id: str):
        try:
            transaction_service.delete_transaction(tx_id)
            return jsonify({"message": "Transaction deleted"})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    return bp
