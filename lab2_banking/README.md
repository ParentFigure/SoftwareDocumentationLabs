# Лабораторна 3 — MVC веб-додаток для онлайн-банкінгу

## Що реалізовано

На основі лабораторної 2 побудовано MVC веб-додаток для предметної області **BNB Paribas online banking**.

### Чому основна сутність саме рахунок

Предметна область збережена навмисно: **основною сутністю лишається банківський рахунок**.
Саме рахунок є центром бізнес-логіки онлайн-банкінгу, тому що:
- рахунок належить конкретному клієнту;
- до рахунку прив'язуються картки;
- по рахунку проходять транзакції;
- баланс, валюта та IBAN є базовими характеристиками, навколо яких будуються інші операції.

Тому навіть після додавання окремих сторінок для карток і транзакцій логіка предметної області не змінюється: **картки і транзакції є похідними сутностями від рахунку**.

## MVC структура

- **Model**: SQLAlchemy-моделі `User`, `Customer`, `Account`, `Card`, `Transaction`
- **Business logic**: `AccountService`, `CardService`, `TransactionService`
- **Controllers**:
  - `account_controller.py`
  - `card_controller.py`
  - `transaction_controller.py`
  - `api_controller.py`
- **Views**: HTML-шаблони Jinja2 у папці `templates`

## Реалізовані можливості

### HTML MVC сторінки
- список рахунків, карток, транзакцій;
- деталі рахунку, картки, транзакції;
- створення, редагування, видалення рахунків;
- створення, редагування, видалення карток;
- створення, редагування, видалення транзакцій.

### REST API з різними HTTP-методами
Реалізовано додаткові варіації запитів `GET / POST / PUT / DELETE`:

#### Accounts
- `GET /api/accounts`
- `GET /api/accounts/<id>`
- `POST /api/accounts`
- `PUT /api/accounts/<id>`
- `DELETE /api/accounts/<id>`

#### Cards
- `GET /api/cards`
- `GET /api/cards/<id>`
- `POST /api/cards`
- `PUT /api/cards/<id>`
- `DELETE /api/cards/<id>`

#### Transactions
- `GET /api/transactions`
- `GET /api/transactions/<id>`
- `POST /api/transactions`
- `PUT /api/transactions/<id>`
- `DELETE /api/transactions/<id>`

## Запуск

```bash
pip install -r requirements.txt
python app.py
```

Відкрити у браузері:

```bash
http://127.0.0.1:5000/
```

## Приклади JSON для API

### Створення рахунку
```json
{
  "customer_no": "CUST-1001",
  "iban": "UA999999999999999999999999999",
  "currency": "UAH",
  "balance": "1000.50"
}
```

### Створення картки
```json
{
  "account_id": "ACCOUNT_ID",
  "masked_pan": "4444********1111",
  "status": "ACTIVE"
}
```

### Створення транзакції TRANSFER
```json
{
  "account_id": "ACCOUNT_ID",
  "tx_type": "TRANSFER",
  "amount": "250.75",
  "status": "COMPLETED",
  "created_at": "2026-04-03T12:00",
  "target_iban": "UA123456789012345678901234567"
}
```

### Створення транзакції BILL_PAYMENT
```json
{
  "account_id": "ACCOUNT_ID",
  "tx_type": "BILL_PAYMENT",
  "amount": "800.00",
  "status": "PENDING",
  "created_at": "2026-04-03T12:00",
  "bill_id": "BILL-2026-001"
}
```


## Важливо про базу даних

- Додаток тепер завжди працює з файлом `banking_lab2.db`, який лежить в тій самій папці, що й `app.py`.
- Тобто POST/PUT/DELETE реально змінюють саме цей файл БД, а не випадкову SQLite-базу з іншої директорії.
- Поточний шлях до БД можна перевірити через `http://127.0.0.1:5000/debug/db-path`.
- Якщо ти хочеш явно вказати іншу БД, можна задати змінну середовища `BANKING_DB_URL`.


## Оновлення

Додано окремий розділ **Користувачі** з повним CRUD для клієнтів банку: список, перегляд, створення, редагування, видалення. При цьому основною сутністю предметної області залишається **рахунок**, оскільки саме рахунок об'єднує клієнта, картки та транзакції.

### Нові маршрути
- `/users/`
- `/users/create`
- `/users/<user_id>`
- `/users/<user_id>/edit`
- `/users/<user_id>/delete`
- `/api/users`
- `/api/users/<user_id>`
