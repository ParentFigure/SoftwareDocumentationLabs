# Лабораторна 2 — Python, 3-рівнева архітектура

## Що реалізовано
- **Рівень доступу до даних**: ORM на SQLAlchemy + зчитування даних з `.csv`
- **Рівень бізнес-логіки**: сервіс імпорту, який читає CSV, створює моделі та зберігає їх у БД
- **Презентаційний рівень**: тільки інтерфейси, без бізнес-логіки
- **DI / IoC**: `DataImportService` працює через інтерфейси `ICsvReader` та `IBankingRepository`
- **Окремий модуль генерації CSV**: `scripts/generate_csv.py`

## Структура
```text
lab2_banking/
├── business/
│   ├── import_service.py
│   └── interfaces.py
├── data_access/
│   ├── csv_reader.py
│   ├── interfaces.py
│   ├── models.py
│   └── repositories.py
├── presentation/
│   └── interfaces.py
├── scripts/
│   └── generate_csv.py
├── main.py
├── requirements.txt
└── README_ua.md
```

## Формат CSV
Усі дані містяться в **одному файлі**, як і вимагає завдання.
Один рядок CSV містить:
- дані клієнта
- дані рахунку
- дані картки
- дані транзакції

При імпорті сервіс:
1. шукає або створює `Customer`
2. шукає або створює `Account`
3. шукає або створює `Card`
4. створює `Transaction` потрібного підтипу

Тобто дублікати клієнтів/рахунків/карток не створюються.

## Встановлення
```bash
pip install -r requirements.txt
```

## Крок 1. Згенерувати CSV на 1000+ рядків
```bash
python scripts/generate_csv.py --output data/banking_data.csv --rows 1000
```

## Крок 2. Імпортувати дані в SQLite
```bash
python main.py --csv data/banking_data.csv --db sqlite:///banking_lab2.db
```

## Таблиці в БД
- `users`
- `customers`
- `accounts`
- `cards`
- `transactions`
- `transfer_transactions`
- `bill_payment_transactions`

### 1. Чому 3 шари
- `data_access` працює тільки з файлами та БД
- `business` містить правила імпорту
- `presentation` містить лише інтерфейси для майбутнього UI/API

### 2. Де тут інтерфейси
- `ICsvReader`
- `IBankingRepository`
- `IDataImportService`
- `IImportPresenter`

### 3. Де DI
У `main.py` ми створюємо конкретні реалізації і передаємо їх у сервіс:
```python
csv_reader = CsvReader()
repository = SqlAlchemyBankingRepository(connection_string=args.db)
service = DataImportService(csv_reader=csv_reader, repository=repository)
```
`DataImportService` не знає про конкретну реалізацію репозиторія, він знає тільки про інтерфейс.

### 4. Як мапиться UML-діаграма
- `Customer` наслідує `User`
- `Customer` має багато `Account`
- `Account` має багато `Card`
- `Account` має багато `Transaction`
- `TransferTransaction` і `BillPaymentTransaction` наслідують `Transaction`

### 5. Як виконується коректне збереження
CSV зберігає все в одному файлі, але при імпорті дані нормалізуються:
- клієнт з тим самим `customer_no` не дублюється
- рахунок з тим самим `iban` не дублюється
- картка з тим самим `masked_pan` в межах рахунку не дублюється
- транзакції додаються окремо
