from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from business.mvc_interfaces import IAccountService


def create_account_blueprint(account_service: IAccountService) -> Blueprint:
    bp = Blueprint("accounts", __name__, url_prefix="/accounts")

    @bp.route("/")
    def index():
        accounts = account_service.get_all_accounts()
        return render_template("accounts/index.html", accounts=accounts)

    @bp.route("/<account_id>")
    def details(account_id: str):
        account = account_service.get_account_details(account_id)
        if account is None:
            flash("Рахунок не знайдено", "danger")
            return redirect(url_for("accounts.index"))
        return render_template("accounts/details.html", account=account)

    @bp.route("/create", methods=["GET", "POST"])
    def create():
        customers = account_service.get_customer_choices()
        if request.method == "POST":
            form_data = {
                "customer_no": request.form.get("customer_no", ""),
                "iban": request.form.get("iban", ""),
                "currency": request.form.get("currency", ""),
                "balance": request.form.get("balance", "0"),
            }
            try:
                account_service.create_account(form_data)
                flash("Рахунок успішно додано", "success")
                return redirect(url_for("accounts.index"))
            except Exception as exc:
                flash(str(exc), "danger")
                return render_template("accounts/create.html", customers=customers, form=form_data)

        return render_template(
            "accounts/create.html",
            customers=customers,
            form={"customer_no": "", "iban": "", "currency": "EUR", "balance": "0"},
        )

    @bp.route("/<account_id>/edit", methods=["GET", "POST"])
    def edit(account_id: str):
        account = account_service.get_account_details(account_id)
        if account is None:
            flash("Рахунок не знайдено", "danger")
            return redirect(url_for("accounts.index"))

        if request.method == "POST":
            form_data = {
                "customer_no": account["customer_no"],
                "iban": request.form.get("iban", ""),
                "currency": request.form.get("currency", ""),
                "balance": request.form.get("balance", "0"),
            }
            try:
                account_service.update_account(account_id, form_data)
                flash("Рахунок успішно змінено", "success")
                return redirect(url_for("accounts.details", account_id=account_id))
            except Exception as exc:
                flash(str(exc), "danger")
                account.update(form_data)
                return render_template("accounts/edit.html", account=account)

        return render_template("accounts/edit.html", account=account)

    @bp.route("/<account_id>/delete", methods=["GET", "POST"])
    def delete(account_id: str):
        account = account_service.get_account_details(account_id)
        if account is None:
            flash("Рахунок не знайдено", "danger")
            return redirect(url_for("accounts.index"))

        if request.method == "POST":
            try:
                account_service.delete_account(account_id)
                flash("Рахунок успішно видалено", "success")
            except Exception as exc:
                flash(str(exc), "danger")
                return redirect(url_for("accounts.details", account_id=account_id))
            return redirect(url_for("accounts.index"))

        return render_template("accounts/delete.html", account=account)

    return bp
