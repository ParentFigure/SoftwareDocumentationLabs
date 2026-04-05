from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from data_access.interfaces import IBankingRepository
from data_access.models import (
    Account,
    Base,
    BillPaymentTransaction,
    Card,
    CardStatus,
    Customer,
    User,
    Transaction,
    TransferTransaction,
    TxStatus,
)


class SqlAlchemyBankingRepository(IBankingRepository):
    def __init__(self, connection_string: str = "sqlite:///banking_lab2.db") -> None:
        self.connection_string = self._normalize_connection_string(connection_string)
        self._engine = create_engine(self.connection_string, echo=False)
        self._session_factory = sessionmaker(bind=self._engine)
        self._session: Session = self._session_factory()

    def init_db(self) -> None:
        Base.metadata.create_all(self._engine)

    def _normalize_connection_string(self, connection_string: str) -> str:
        prefix = "sqlite:///"
        if not connection_string.startswith(prefix):
            return connection_string

        db_part = connection_string[len(prefix):]
        if db_part == ":memory:" or Path(db_part).is_absolute():
            return connection_string

        absolute_path = (Path(__file__).resolve().parent.parent / db_part).resolve()
        return f"sqlite:///{absolute_path.as_posix()}"

    def get_or_create_customer(
        self,
        customer_no: str,
        full_name: str,
        phone: str,
        email: str,
        password_hash: str,
    ) -> Customer:
        customer = self._session.scalar(select(Customer).where(Customer.customer_no == customer_no))
        if customer:
            customer.full_name = full_name
            customer.phone = phone
            customer.email = email
            customer.password_hash = password_hash
            return customer

        customer = Customer(
            customer_no=customer_no,
            full_name=full_name,
            phone=phone,
            email=email,
            password_hash=password_hash,
        )
        self._session.add(customer)
        self._session.flush()
        return customer

    def get_or_create_account(self, customer_no: str, iban: str, currency: str, balance: float) -> Account:
        account = self._session.scalar(select(Account).where(Account.iban == iban))
        if account:
            account.currency = currency
            account.balance = balance
            return account

        customer = self._session.scalar(select(Customer).where(Customer.customer_no == customer_no))
        if not customer:
            raise ValueError(f"Customer with number {customer_no} does not exist")

        account = Account(customer_id=customer.user_id, iban=iban, currency=currency, balance=balance)
        self._session.add(account)
        self._session.flush()
        return account

    def get_or_create_card(self, account_iban: str, masked_pan: str, status: str) -> Card:
        account = self._session.scalar(select(Account).where(Account.iban == account_iban))
        if not account:
            raise ValueError(f"Account with IBAN {account_iban} does not exist")

        card = self._session.scalar(select(Card).where(Card.account_id == account.account_id, Card.masked_pan == masked_pan))
        enum_status = CardStatus(status)
        if card:
            card.status = enum_status
            return card

        card = Card(account_id=account.account_id, masked_pan=masked_pan, status=enum_status)
        self._session.add(card)
        self._session.flush()
        return card

    def add_transaction(
        self,
        account_iban: str,
        tx_type: str,
        amount: float,
        status: str,
        created_at: str,
        target_iban: str | None = None,
        bill_id: str | None = None,
    ) -> Transaction:
        account = self._session.scalar(select(Account).where(Account.iban == account_iban))
        if not account:
            raise ValueError(f"Account with IBAN {account_iban} does not exist")
        return self._build_transaction(
            account_id=account.account_id,
            tx_type=tx_type,
            amount=amount,
            status=status,
            created_at=created_at,
            target_iban=target_iban,
            bill_id=bill_id,
        )

    def list_users(self) -> list[dict]:
        users = self._session.scalars(select(Customer).order_by(Customer.full_name)).all()
        return [self._user_payload(user) for user in users]

    def get_user_details(self, user_id: str) -> dict | None:
        user = self._session.get(Customer, user_id)
        return self._user_payload(user, include_accounts=True) if user else None

    def create_user(
        self,
        customer_no: str,
        full_name: str,
        phone: str,
        email: str,
        password_hash: str,
    ):
        duplicate_no = self._session.scalar(select(Customer).where(Customer.customer_no == customer_no))
        if duplicate_no:
            raise ValueError("Клієнт з таким номером уже існує")
        duplicate_email = self._session.scalar(select(User).where(User.email == email))
        if duplicate_email:
            raise ValueError("Користувач з таким email уже існує")
        user = Customer(
            customer_no=customer_no,
            full_name=full_name,
            phone=phone,
            email=email,
            password_hash=password_hash,
        )
        self._session.add(user)
        self._session.flush()
        return user

    def update_user(
        self,
        user_id: str,
        customer_no: str,
        full_name: str,
        phone: str,
        email: str,
        password_hash: str,
    ):
        user = self._session.get(Customer, user_id)
        if not user:
            raise ValueError("Користувача не знайдено")
        duplicate_no = self._session.scalar(select(Customer).where(Customer.customer_no == customer_no, Customer.user_id != user_id))
        if duplicate_no:
            raise ValueError("Інший клієнт уже має такий номер")
        duplicate_email = self._session.scalar(select(User).where(User.email == email, User.user_id != user_id))
        if duplicate_email:
            raise ValueError("Інший користувач уже має такий email")
        user.customer_no = customer_no
        user.full_name = full_name
        user.phone = phone
        user.email = email
        user.password_hash = password_hash
        self._session.flush()
        return user

    def delete_user(self, user_id: str) -> None:
        user = self._session.get(Customer, user_id)
        if not user:
            raise ValueError("Користувача не знайдено")
        if user.accounts:
            raise ValueError("Не можна видалити користувача, поки в нього є рахунки")
        self._session.delete(user)
        self._session.flush()

    def list_accounts(self) -> list[dict]:
        accounts = self._session.scalars(select(Account).order_by(Account.iban)).all()
        result: list[dict] = []
        for account in accounts:
            customer = account.customer
            result.append(
                {
                    "account_id": account.account_id,
                    "customer_no": customer.customer_no,
                    "full_name": customer.full_name,
                    "iban": account.iban,
                    "currency": account.currency,
                    "balance": account.balance,
                    "card_count": len(account.cards),
                    "transaction_count": len(account.transactions),
                }
            )
        return result

    def get_account_details(self, account_id: str) -> dict | None:
        account = self._session.get(Account, account_id)
        if not account:
            return None
        return {
            "account_id": account.account_id,
            "customer_no": account.customer.customer_no,
            "full_name": account.customer.full_name,
            "iban": account.iban,
            "currency": account.currency,
            "balance": account.balance,
            "cards": [self._card_payload(c) for c in account.cards],
            "transactions": [self._transaction_payload(tx) for tx in sorted(account.transactions, key=lambda item: item.created_at, reverse=True)[:10]],
        }

    def create_account(self, customer_no: str, iban: str, currency: str, balance: float):
        existing = self._session.scalar(select(Account).where(Account.iban == iban))
        if existing:
            raise ValueError("Рахунок з таким IBAN вже існує")
        customer = self._session.scalar(select(Customer).where(Customer.customer_no == customer_no))
        if not customer:
            raise ValueError("Клієнта не знайдено")
        account = Account(customer_id=customer.user_id, iban=iban, currency=currency, balance=balance)
        self._session.add(account)
        self._session.flush()
        return account

    def update_account(self, account_id: str, iban: str, currency: str, balance: float):
        account = self._session.get(Account, account_id)
        if not account:
            raise ValueError("Рахунок не знайдено")
        duplicate = self._session.scalar(select(Account).where(Account.iban == iban, Account.account_id != account_id))
        if duplicate:
            raise ValueError("Інший рахунок вже має такий IBAN")
        account.iban = iban
        account.currency = currency
        account.balance = balance
        self._session.flush()
        return account

    def delete_account(self, account_id: str) -> None:
        account = self._session.get(Account, account_id)
        if not account:
            raise ValueError("Рахунок не знайдено")
        self._session.delete(account)
        self._session.flush()

    def list_customers(self) -> list[dict]:
        customers = self._session.scalars(select(Customer).order_by(Customer.full_name)).all()
        return [{"customer_no": customer.customer_no, "full_name": customer.full_name} for customer in customers]

    def list_account_choices(self) -> list[dict]:
        accounts = self._session.scalars(select(Account).order_by(Account.iban)).all()
        return [
            {
                "account_id": account.account_id,
                "iban": account.iban,
                "customer_no": account.customer.customer_no,
                "full_name": account.customer.full_name,
            }
            for account in accounts
        ]

    def list_cards(self) -> list[dict]:
        cards = self._session.scalars(select(Card).order_by(Card.masked_pan)).all()
        return [self._card_payload(card) for card in cards]

    def get_card_details(self, card_id: str) -> dict | None:
        card = self._session.get(Card, card_id)
        return self._card_payload(card) if card else None

    def create_card(self, account_id: str, masked_pan: str, status: str):
        account = self._session.get(Account, account_id)
        if not account:
            raise ValueError("Рахунок не знайдено")
        duplicate = self._session.scalar(select(Card).where(Card.account_id == account_id, Card.masked_pan == masked_pan))
        if duplicate:
            raise ValueError("На цьому рахунку вже існує картка з таким номером")
        card = Card(account_id=account_id, masked_pan=masked_pan, status=CardStatus(status))
        self._session.add(card)
        self._session.flush()
        return card

    def update_card(self, card_id: str, account_id: str, masked_pan: str, status: str):
        card = self._session.get(Card, card_id)
        if not card:
            raise ValueError("Картку не знайдено")
        account = self._session.get(Account, account_id)
        if not account:
            raise ValueError("Рахунок не знайдено")
        duplicate = self._session.scalar(select(Card).where(Card.account_id == account_id, Card.masked_pan == masked_pan, Card.card_id != card_id))
        if duplicate:
            raise ValueError("На цьому рахунку вже є інша картка з таким номером")
        card.account_id = account_id
        card.masked_pan = masked_pan
        card.status = CardStatus(status)
        self._session.flush()
        return card

    def delete_card(self, card_id: str) -> None:
        card = self._session.get(Card, card_id)
        if not card:
            raise ValueError("Картку не знайдено")
        self._session.delete(card)
        self._session.flush()

    def list_transactions(self) -> list[dict]:
        txs = self._session.scalars(select(Transaction).order_by(Transaction.created_at.desc())).all()
        return [self._transaction_payload(tx) for tx in txs]

    def get_transaction_details(self, tx_id: str) -> dict | None:
        tx = self._session.get(Transaction, tx_id)
        return self._transaction_payload(tx) if tx else None

    def create_transaction(
        self,
        account_id: str,
        tx_type: str,
        amount: float,
        status: str,
        created_at: str | None = None,
        target_iban: str | None = None,
        bill_id: str | None = None,
    ):
        if not self._session.get(Account, account_id):
            raise ValueError("Рахунок не знайдено")
        return self._build_transaction(account_id, tx_type, amount, status, created_at, target_iban, bill_id)

    def update_transaction(
        self,
        tx_id: str,
        account_id: str,
        tx_type: str,
        amount: float,
        status: str,
        created_at: str | None = None,
        target_iban: str | None = None,
        bill_id: str | None = None,
    ):
        tx = self._session.get(Transaction, tx_id)
        if not tx:
            raise ValueError("Транзакцію не знайдено")
        if not self._session.get(Account, account_id):
            raise ValueError("Рахунок не знайдено")

        if tx.tx_type != tx_type:
            self._session.delete(tx)
            self._session.flush()
            new_tx = self._build_transaction(account_id, tx_type, amount, status, created_at, target_iban, bill_id, tx_id=tx_id)
            self._session.flush()
            return new_tx

        tx.account_id = account_id
        tx.amount = amount
        tx.status = TxStatus(status)
        tx.created_at = self._parse_datetime(created_at)
        if isinstance(tx, TransferTransaction):
            if not target_iban:
                raise ValueError("Для переказу потрібен IBAN отримувача")
            tx.to_iban = target_iban
        elif isinstance(tx, BillPaymentTransaction):
            if not bill_id:
                raise ValueError("Для оплати рахунку потрібен bill_id")
            tx.bill_id = bill_id
        self._session.flush()
        return tx

    def delete_transaction(self, tx_id: str) -> None:
        tx = self._session.get(Transaction, tx_id)
        if not tx:
            raise ValueError("Транзакцію не знайдено")
        self._session.delete(tx)
        self._session.flush()

    def _build_transaction(
        self,
        account_id: str,
        tx_type: str,
        amount: float,
        status: str,
        created_at: str | None,
        target_iban: str | None = None,
        bill_id: str | None = None,
        tx_id: str | None = None,
    ) -> Transaction:
        parsed_dt = self._parse_datetime(created_at)
        enum_status = TxStatus(status)

        if tx_type == "TRANSFER":
            if not target_iban:
                raise ValueError("TRANSFER transaction requires target_iban")
            tx = TransferTransaction(
                tx_id=tx_id,
                account_id=account_id,
                amount=amount,
                status=enum_status,
                created_at=parsed_dt,
                to_iban=target_iban,
            )
        elif tx_type == "BILL_PAYMENT":
            if not bill_id:
                raise ValueError("BILL_PAYMENT transaction requires bill_id")
            tx = BillPaymentTransaction(
                tx_id=tx_id,
                account_id=account_id,
                amount=amount,
                status=enum_status,
                created_at=parsed_dt,
                bill_id=bill_id,
            )
        else:
            raise ValueError(f"Unsupported transaction type: {tx_type}")

        self._session.add(tx)
        self._session.flush()
        return tx

    def _parse_datetime(self, created_at: str | None) -> datetime:
        return datetime.fromisoformat(created_at) if created_at else datetime.utcnow()

    def _user_payload(self, user: Customer, include_accounts: bool = False) -> dict:
        payload = {
            "user_id": user.user_id,
            "customer_no": user.customer_no,
            "full_name": user.full_name,
            "phone": user.phone,
            "email": user.email,
            "password_hash": user.password_hash,
            "account_count": len(user.accounts),
        }
        if include_accounts:
            payload["accounts"] = [
                {
                    "account_id": account.account_id,
                    "iban": account.iban,
                    "currency": account.currency,
                    "balance": account.balance,
                }
                for account in sorted(user.accounts, key=lambda item: item.iban)
            ]
        return payload

    def _card_payload(self, card: Card) -> dict:
        return {
            "card_id": card.card_id,
            "account_id": card.account_id,
            "iban": card.account.iban,
            "customer_no": card.account.customer.customer_no,
            "full_name": card.account.customer.full_name,
            "masked_pan": card.masked_pan,
            "status": card.status.value if hasattr(card.status, "value") else str(card.status),
        }

    def _transaction_payload(self, tx: Transaction) -> dict:
        extra = "-"
        target_iban = None
        bill_id = None
        if isinstance(tx, TransferTransaction):
            target_iban = tx.to_iban
            extra = f"IBAN отримувача: {tx.to_iban}"
        elif isinstance(tx, BillPaymentTransaction):
            bill_id = tx.bill_id
            extra = f"Рахунок на оплату: {tx.bill_id}"
        return {
            "tx_id": tx.tx_id,
            "account_id": tx.account_id,
            "iban": tx.account.iban,
            "customer_no": tx.account.customer.customer_no,
            "full_name": tx.account.customer.full_name,
            "created_at": tx.created_at.strftime("%Y-%m-%d %H:%M"),
            "created_at_input": tx.created_at.strftime("%Y-%m-%dT%H:%M"),
            "tx_type": tx.tx_type,
            "amount": tx.amount,
            "status": tx.status.value if hasattr(tx.status, "value") else str(tx.status),
            "extra": extra,
            "target_iban": target_iban,
            "bill_id": bill_id,
        }

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def close(self) -> None:
        self._session.close()
