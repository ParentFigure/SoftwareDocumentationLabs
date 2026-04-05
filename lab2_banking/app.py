from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, redirect, url_for

from business.account_service import AccountService
from business.card_service import CardService
from business.transaction_service import TransactionService
from business.user_service import UserService
from controllers.account_controller import create_account_blueprint
from controllers.api_controller import create_api_blueprint
from controllers.card_controller import create_card_blueprint
from controllers.transaction_controller import create_transaction_blueprint
from controllers.user_controller import create_user_blueprint
from data_access.repositories import SqlAlchemyBankingRepository


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DB_FILE = PROJECT_DIR / "banking_lab2.db"
DEFAULT_DB = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "lab3-secret-key"

    db_url = os.getenv("BANKING_DB_URL", DEFAULT_DB)
    repository = SqlAlchemyBankingRepository(connection_string=db_url)
    repository.init_db()

    account_service = AccountService(repository)
    card_service = CardService(repository)
    transaction_service = TransactionService(repository)
    user_service = UserService(repository)

    app.register_blueprint(create_account_blueprint(account_service))
    app.register_blueprint(create_card_blueprint(card_service))
    app.register_blueprint(create_user_blueprint(user_service))
    app.register_blueprint(create_transaction_blueprint(transaction_service))
    app.register_blueprint(create_api_blueprint(account_service, card_service, transaction_service, user_service))

    @app.route("/")
    def home():
        return redirect(url_for("accounts.index"))

    @app.route("/debug/db-path")
    def debug_db_path():
        return {"database_url": repository.connection_string, "project_dir": str(PROJECT_DIR)}

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        repository.close()

    print(f"[Lab3 MVC] Using database: {repository.connection_string}")
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
