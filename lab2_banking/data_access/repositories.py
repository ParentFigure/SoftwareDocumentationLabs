from __future__ import annotations

from datetime import datetime

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
    Transaction,
    TransferTransaction,
    TxStatus,
)


class SqlAlchemyBankingRepository(IBankingRepository):
    def __init__(self, connection_string: str = "sqlite:///banking_lab2.db") -> None:
        self._engine = create_engine(connection_string, echo=False)
        self._session_factory = sessionmaker(bind=self._engine)
        self._session: Session = self._session_factory()

    def init_db(self) -> None:
        Base.metadata.create_all(self._engine)

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

    def get_or_create_account(
        self,
        customer_no: str,
        iban: str,
        currency: str,
        balance: float,
    ) -> Account:
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

        card = self._session.scalar(
            select(Card).where(Card.account_id == account.account_id, Card.masked_pan == masked_pan)
        )
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

        parsed_dt = datetime.fromisoformat(created_at)
        enum_status = TxStatus(status)

        if tx_type == "TRANSFER":
            if not target_iban:
                raise ValueError("TRANSFER transaction requires target_iban")
            tx = TransferTransaction(
                account_id=account.account_id,
                amount=amount,
                status=enum_status,
                created_at=parsed_dt,
                to_iban=target_iban,
            )
        elif tx_type == "BILL_PAYMENT":
            if not bill_id:
                raise ValueError("BILL_PAYMENT transaction requires bill_id")
            tx = BillPaymentTransaction(
                account_id=account.account_id,
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

    def commit(self) -> None:
        self._session.commit()

    def close(self) -> None:
        self._session.close()
