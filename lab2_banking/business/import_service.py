from __future__ import annotations

from data_access.interfaces import IBankingRepository, ICsvReader
from business.interfaces import IDataImportService


class DataImportService(IDataImportService):
    REQUIRED_COLUMNS = {
        "customer_no",
        "full_name",
        "phone",
        "email",
        "password_hash",
        "account_iban",
        "currency",
        "balance",
        "card_masked_pan",
        "card_status",
        "tx_type",
        "amount",
        "tx_status",
        "created_at",
        "target_iban",
        "bill_id",
    }

    def __init__(self, csv_reader: ICsvReader, repository: IBankingRepository) -> None:
        self._csv_reader = csv_reader
        self._repository = repository

    def import_from_csv(self, csv_path: str) -> dict[str, int]:
        rows = self._csv_reader.read_rows(csv_path)
        missing = self.REQUIRED_COLUMNS.difference(rows[0].keys())
        if missing:
            raise ValueError(f"CSV file is missing columns: {', '.join(sorted(missing))}")

        self._repository.init_db()

        customers: set[str] = set()
        accounts: set[str] = set()
        cards: set[tuple[str, str]] = set()
        tx_count = 0

        for row in rows:
            self._repository.get_or_create_customer(
                customer_no=row["customer_no"],
                full_name=row["full_name"],
                phone=row["phone"],
                email=row["email"],
                password_hash=row["password_hash"],
            )
            customers.add(row["customer_no"])

            self._repository.get_or_create_account(
                customer_no=row["customer_no"],
                iban=row["account_iban"],
                currency=row["currency"],
                balance=float(row["balance"]),
            )
            accounts.add(row["account_iban"])

            self._repository.get_or_create_card(
                account_iban=row["account_iban"],
                masked_pan=row["card_masked_pan"],
                status=row["card_status"],
            )
            cards.add((row["account_iban"], row["card_masked_pan"]))

            self._repository.add_transaction(
                account_iban=row["account_iban"],
                tx_type=row["tx_type"],
                amount=float(row["amount"]),
                status=row["tx_status"],
                created_at=row["created_at"],
                target_iban=row["target_iban"] or None,
                bill_id=row["bill_id"] or None,
            )
            tx_count += 1

        self._repository.commit()
        return {
            "customers": len(customers),
            "accounts": len(accounts),
            "cards": len(cards),
            "transactions": tx_count,
        }
