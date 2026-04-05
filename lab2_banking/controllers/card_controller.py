from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from business.mvc_interfaces import ICardService


STATUSES = ["ACTIVE", "BLOCKED"]


def create_card_blueprint(card_service: ICardService) -> Blueprint:
    bp = Blueprint("cards", __name__, url_prefix="/cards")

    @bp.route("/")
    def index():
        return render_template("cards/index.html", cards=card_service.get_all_cards())

    @bp.route("/<card_id>")
    def details(card_id: str):
        card = card_service.get_card_details(card_id)
        if not card:
            flash("Картку не знайдено", "danger")
            return redirect(url_for("cards.index"))
        return render_template("cards/details.html", card=card)

    @bp.route("/create", methods=["GET", "POST"])
    def create():
        accounts = card_service.get_account_choices()
        form = {"account_id": "", "masked_pan": "", "status": "ACTIVE"}
        if request.method == "POST":
            form = {k: request.form.get(k, "") for k in form}
            try:
                card_service.create_card(form)
                flash("Картку успішно додано", "success")
                return redirect(url_for("cards.index"))
            except Exception as exc:
                flash(str(exc), "danger")
        return render_template("cards/create.html", form=form, accounts=accounts, statuses=STATUSES)

    @bp.route("/<card_id>/edit", methods=["GET", "POST"])
    def edit(card_id: str):
        card = card_service.get_card_details(card_id)
        if not card:
            flash("Картку не знайдено", "danger")
            return redirect(url_for("cards.index"))
        if request.method == "POST":
            form = {"account_id": request.form.get("account_id", ""), "masked_pan": request.form.get("masked_pan", ""), "status": request.form.get("status", "")}
            try:
                card_service.update_card(card_id, form)
                flash("Картку успішно змінено", "success")
                return redirect(url_for("cards.details", card_id=card_id))
            except Exception as exc:
                flash(str(exc), "danger")
                card.update(form)
        return render_template("cards/edit.html", card=card, accounts=card_service.get_account_choices(), statuses=STATUSES)

    @bp.route("/<card_id>/delete", methods=["GET", "POST"])
    def delete(card_id: str):
        card = card_service.get_card_details(card_id)
        if not card:
            flash("Картку не знайдено", "danger")
            return redirect(url_for("cards.index"))
        if request.method == "POST":
            try:
                card_service.delete_card(card_id)
                flash("Картку успішно видалено", "success")
                return redirect(url_for("cards.index"))
            except Exception as exc:
                flash(str(exc), "danger")
                return redirect(url_for("cards.details", card_id=card_id))
        return render_template("cards/delete.html", card=card)

    return bp
