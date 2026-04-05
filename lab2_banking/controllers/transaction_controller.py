from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from business.mvc_interfaces import ITransactionService


TX_TYPES = ["TRANSFER", "BILL_PAYMENT"]
STATUSES = ["PENDING", "COMPLETED", "FAILED"]


def create_transaction_blueprint(transaction_service: ITransactionService) -> Blueprint:
    bp = Blueprint("transactions", __name__, url_prefix="/transactions")

    @bp.route("/")
    def index():
        return render_template("transactions/index.html", transactions=transaction_service.get_all_transactions())

    @bp.route("/<tx_id>")
    def details(tx_id: str):
        tx = transaction_service.get_transaction_details(tx_id)
        if not tx:
            flash("Транзакцію не знайдено", "danger")
            return redirect(url_for("transactions.index"))
        return render_template("transactions/details.html", tx=tx)

    @bp.route("/create", methods=["GET", "POST"])
    def create():
        accounts = transaction_service.get_account_choices()
        form = {
            "account_id": "",
            "tx_type": "TRANSFER",
            "amount": "0",
            "status": "COMPLETED",
            "created_at": "",
            "target_iban": "",
            "bill_id": "",
        }
        if request.method == "POST":
            form = {k: request.form.get(k, "") for k in form}
            try:
                transaction_service.create_transaction(form)
                flash("Транзакцію успішно додано", "success")
                return redirect(url_for("transactions.index"))
            except Exception as exc:
                flash(str(exc), "danger")
        return render_template("transactions/create.html", form=form, accounts=accounts, tx_types=TX_TYPES, statuses=STATUSES)

    @bp.route("/<tx_id>/edit", methods=["GET", "POST"])
    def edit(tx_id: str):
        tx = transaction_service.get_transaction_details(tx_id)
        if not tx:
            flash("Транзакцію не знайдено", "danger")
            return redirect(url_for("transactions.index"))
        if request.method == "POST":
            form = {
                "account_id": request.form.get("account_id", ""),
                "tx_type": request.form.get("tx_type", ""),
                "amount": request.form.get("amount", ""),
                "status": request.form.get("status", ""),
                "created_at": request.form.get("created_at", ""),
                "target_iban": request.form.get("target_iban", ""),
                "bill_id": request.form.get("bill_id", ""),
            }
            try:
                transaction_service.update_transaction(tx_id, form)
                flash("Транзакцію успішно змінено", "success")
                return redirect(url_for("transactions.details", tx_id=tx_id))
            except Exception as exc:
                flash(str(exc), "danger")
                tx.update(form)
        return render_template("transactions/edit.html", tx=tx, accounts=transaction_service.get_account_choices(), tx_types=TX_TYPES, statuses=STATUSES)

    @bp.route("/<tx_id>/delete", methods=["GET", "POST"])
    def delete(tx_id: str):
        tx = transaction_service.get_transaction_details(tx_id)
        if not tx:
            flash("Транзакцію не знайдено", "danger")
            return redirect(url_for("transactions.index"))
        if request.method == "POST":
            try:
                transaction_service.delete_transaction(tx_id)
                flash("Транзакцію успішно видалено", "success")
                return redirect(url_for("transactions.index"))
            except Exception as exc:
                flash(str(exc), "danger")
                return redirect(url_for("transactions.details", tx_id=tx_id))
        return render_template("transactions/delete.html", tx=tx)

    return bp
