from __future__ import annotations

import argparse

from business.import_service import DataImportService
from data_access.csv_reader import CsvReader
from data_access.repositories import SqlAlchemyBankingRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Import banking data from CSV into SQLite database.")
    parser.add_argument("--csv", default="data/banking_data.csv", help="Path to source CSV file")
    parser.add_argument(
        "--db",
        default="sqlite:///banking_lab2.db",
        help="SQLAlchemy connection string, for example sqlite:///banking_lab2.db",
    )
    args = parser.parse_args()

    csv_reader = CsvReader()
    repository = SqlAlchemyBankingRepository(connection_string=args.db)
    service = DataImportService(csv_reader=csv_reader, repository=repository)

    try:
        stats = service.import_from_csv(args.csv)
        print("Import completed successfully")
        for key, value in stats.items():
            print(f"- {key}: {value}")
    finally:
        repository.close()


if __name__ == "__main__":
    main()
