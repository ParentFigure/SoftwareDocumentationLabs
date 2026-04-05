from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CardStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class TxStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": type,
    }


class Customer(User):
    __tablename__ = "customers"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    customer_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    accounts: Mapped[list["Account"]] = relationship(back_populates="customer", cascade="all, delete-orphan")

    __mapper_args__ = {"polymorphic_identity": "customer"}


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.user_id"), nullable=False)
    iban: Mapped[str] = mapped_column(String(34), unique=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    customer: Mapped[Customer] = relationship(back_populates="accounts")
    cards: Mapped[list["Card"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account", cascade="all, delete-orphan")


class Card(Base):
    __tablename__ = "cards"

    card_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id"), nullable=False)
    masked_pan: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[CardStatus] = mapped_column(Enum(CardStatus), nullable=False)

    account: Mapped[Account] = relationship(back_populates="cards")


class Transaction(Base):
    __tablename__ = "transactions"

    tx_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    status: Mapped[TxStatus] = mapped_column(Enum(TxStatus), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    tx_type: Mapped[str] = mapped_column(String(50), nullable=False)

    account: Mapped[Account] = relationship(back_populates="transactions")

    __mapper_args__ = {
        "polymorphic_identity": "transaction",
        "polymorphic_on": tx_type,
    }


class TransferTransaction(Transaction):
    __tablename__ = "transfer_transactions"

    tx_id: Mapped[str] = mapped_column(ForeignKey("transactions.tx_id"), primary_key=True)
    to_iban: Mapped[str] = mapped_column(String(34), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "TRANSFER"}


class BillPaymentTransaction(Transaction):
    __tablename__ = "bill_payment_transactions"

    tx_id: Mapped[str] = mapped_column(ForeignKey("transactions.tx_id"), primary_key=True)
    bill_id: Mapped[str] = mapped_column(String(50), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "BILL_PAYMENT"}
