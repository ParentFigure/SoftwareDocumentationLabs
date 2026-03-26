from __future__ import annotations

import argparse
import csv
import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path

CARD_STATUSES = ["ACTIVE", "BLOCKED"]
TX_STATUSES = ["PENDING", "COMPLETED", "FAILED"]
TX_TYPES = ["TRANSFER", "BILL_PAYMENT"]
CURRENCIES = ["UAH", "USD", "EUR"]
FIRST_NAMES = ["Ivan", "Olena", "Maksym", "Sofiia", "Andrii", "Kateryna", "Dmytro", "Iryna"]
LAST_NAMES = ["Shevchenko", "Koval", "Tkachenko", "Melnyk", "Bondarenko", "Tkachuk"]


def masked_pan(index: int) -> str:
    return f"**** **** **** {1000 + index % 9000}"


def iban(index: int) -> str:
    return f"UA{str(10_000_000_000_000_000_000_000 + index).zfill(27)}"[:29]


def build_rows(count: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    random.seed(42)
    base_time = datetime(2024, 1, 1, 9, 0, 0)

    customer_count = max(100, count // 10)
    customers = []
    for i in range(customer_count):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}{i}@example.com"
        customers.append(
            {
                "customer_no": f"CUST-{1000 + i}",
                "full_name": f"{first} {last}",
                "phone": f"+38067{1000000 + i}",
                "email": email,
                "password_hash": hashlib.sha256(f"pass{i}".encode()).hexdigest(),
            }
        )

    accounts = []
    for i, customer in enumerate(customers):
        for j in range(1, 3):
            accounts.append(
                {
                    **customer,
                    "account_iban": iban(i * 2 + j),
                    "currency": random.choice(CURRENCIES),
                    "balance": round(random.uniform(1000, 100000), 2),
                    "card_masked_pan": masked_pan(i * 2 + j),
                    "card_status": random.choice(CARD_STATUSES),
                }
            )

    for idx in range(count):
        account = random.choice(accounts)
        tx_type = random.choice(TX_TYPES)
        tx_time = (base_time + timedelta(minutes=idx * 7)).isoformat()
        row = {
            **account,
            "balance": str(account["balance"]),
            "tx_type": tx_type,
            "amount": str(round(random.uniform(50, 15000), 2)),
            "tx_status": random.choice(TX_STATUSES),
            "created_at": tx_time,
            "target_iban": "",
            "bill_id": "",
        }
        if tx_type == "TRANSFER":
            target = random.choice(accounts)
            while target["account_iban"] == account["account_iban"]:
                target = random.choice(accounts)
            row["target_iban"] = target["account_iban"]
        else:
            row["bill_id"] = f"BILL-{50000 + idx}"
        rows.append(row)

    return rows


def write_csv(path: str, count: int) -> None:
    rows = build_rows(count)
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate one CSV file with banking data.")
    parser.add_argument("--output", default="data/banking_data.csv", help="Path to CSV file")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows to generate")
    args = parser.parse_args()

    if args.rows < 1000:
        raise SystemExit("The assignment requires at least 1000 rows.")

    write_csv(args.output, args.rows)
    print(f"CSV generated: {args.output} ({args.rows} rows)")
