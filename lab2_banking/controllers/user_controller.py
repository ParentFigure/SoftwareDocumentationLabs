from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from business.mvc_interfaces import IUserService



def create_user_blueprint(user_service: IUserService) -> Blueprint:
    bp = Blueprint("users", __name__, url_prefix="/users")

    @bp.route("/")
    def index():
        users = user_service.get_all_users()
        return render_template("users/index.html", users=users)

    @bp.route("/create", methods=["GET", "POST"])
    def create():
        if request.method == "POST":
            form_data = {
                "customer_no": request.form.get("customer_no", ""),
                "full_name": request.form.get("full_name", ""),
                "phone": request.form.get("phone", ""),
                "email": request.form.get("email", ""),
                "password_hash": request.form.get("password_hash", ""),
            }
            try:
                user_service.create_user(form_data)
                flash("Користувача успішно додано", "success")
                return redirect(url_for("users.index"))
            except Exception as exc:
                flash(str(exc), "danger")
                return render_template("users/create.html", user=form_data)

        return render_template(
            "users/create.html",
            user={"customer_no": "", "full_name": "", "phone": "", "email": "", "password_hash": "default_hash"},
        )

    @bp.route("/<user_id>")
    def details(user_id: str):
        user = user_service.get_user_details(user_id)
        if user is None:
            flash("Користувача не знайдено", "danger")
            return redirect(url_for("users.index"))
        return render_template("users/details.html", user=user)

    @bp.route("/<user_id>/edit", methods=["GET", "POST"])
    def edit(user_id: str):
        user = user_service.get_user_details(user_id)
        if user is None:
            flash("Користувача не знайдено", "danger")
            return redirect(url_for("users.index"))

        if request.method == "POST":
            form_data = {
                "customer_no": request.form.get("customer_no", ""),
                "full_name": request.form.get("full_name", ""),
                "phone": request.form.get("phone", ""),
                "email": request.form.get("email", ""),
                "password_hash": request.form.get("password_hash", ""),
            }
            try:
                user_service.update_user(user_id, form_data)
                flash("Користувача успішно змінено", "success")
                return redirect(url_for("users.details", user_id=user_id))
            except Exception as exc:
                flash(str(exc), "danger")
                user.update(form_data)
                return render_template("users/edit.html", user=user)

        return render_template("users/edit.html", user=user)

    @bp.route("/<user_id>/delete", methods=["GET", "POST"])
    def delete(user_id: str):
        user = user_service.get_user_details(user_id)
        if user is None:
            flash("Користувача не знайдено", "danger")
            return redirect(url_for("users.index"))

        if request.method == "POST":
            try:
                user_service.delete_user(user_id)
                flash("Користувача успішно видалено", "success")
                return redirect(url_for("users.index"))
            except Exception as exc:
                flash(str(exc), "danger")
                return redirect(url_for("users.details", user_id=user_id))

        return render_template("users/delete.html", user=user)

    return bp
