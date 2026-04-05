# Лабораторна 4
## Реалізація GoF-паттерну Strategy

Проєкт реалізує патерн **Strategy** для виводу рядків у різні сховища:
- консоль
- файл
- Redis
- Kafka

Перемикання між способами виводу виконується **лише через `config/config.yaml`**, без зміни Python-коду.

## Структура
- `main.py` — точка входу
- `src/dataset_service.py` — завантаження CSV та читання рядків
- `src/output_strategies.py` — конкретні стратегії виводу
- `src/strategy_factory.py` — фабрика створення стратегії
- `config/config.yaml` — конфігурація
- `docker-compose.yml` — запуск Redis і Kafka
- `scripts/check_redis.py` — перевірка, що повідомлення записались у Redis
- `scripts/check_kafka.py` — перевірка, що повідомлення записались у Kafka

## 1. Встановлення залежностей
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Завантаження датасету
Цей проєкт працює з датасетом **Open Parking and Camera Violations** (`nc67-uf89`).
CSV можна отримати через Socrata API endpoint:
`https://data.cityofnewyork.us/resource/nc67-uf89.csv?$limit=20`

Перший запуск зроби з параметром `--download`, щоб CSV був збережений локально у `data/open_parking_and_camera_violations.csv`.

```bash
python main.py --download
```

Після цього локальний файл уже існує, і програму можна запускати без повторного завантаження:

```bash
python main.py
```

## 3. Запуск Redis і Kafka через Docker
Потрібно, щоб на комп'ютері був встановлений **Docker Desktop**.

Запуск:
```bash
docker compose up -d
```

Перевірка контейнерів:
```bash
docker ps
```

У списку мають бути:
- `lab4-redis`
- `lab4-kafka`

Зупинка:
```bash
docker compose down
```

## 4. Перемикання Strategy через config
У файлі `config/config.yaml` змінюється тільки поле:

```yaml
output:
  strategy: "console"
```

Можливі значення:
- `console`
- `file`
- `redis`
- `kafka`

### 4.1 Console
```yaml
output:
  strategy: "console"
```

Запуск:
```bash
python main.py
```

### 4.2 File
```yaml
output:
  strategy: "file"
  file:
    path: "output/violations_output.txt"
```

Запуск:
```bash
python main.py
```

Результат буде в `output/violations_output.txt`.

### 4.3 Redis
Перед запуском Redis-стратегії контейнер Redis повинен бути запущений.

```yaml
output:
  strategy: "redis"
  clear_before_write: true
  redis:
    host: "localhost"
    port: 6379
    db: 0
    list_key: "violations:list"
```

Запуск:
```bash
python main.py
```

Перевірка з Python:
```bash
python scripts/check_redis.py
```

Або через контейнер:
```bash
docker exec -it lab4-redis redis-cli LRANGE violations:list 0 -1
```

### 4.4 Kafka
Перед запуском Kafka-стратегії контейнер Kafka повинен бути запущений.

```yaml
output:
  strategy: "kafka"
  kafka:
    bootstrap_servers: ["localhost:9092"]
    topic: "violations-topic"
    client_id: "lab4-strategy-producer"
```

Запуск:
```bash
python main.py
```

Перевірка з Python consumer:
```bash
python scripts/check_kafka.py
```

## 5. Що саме демонструє Strategy
- `DatasetService` займається тільки завантаженням і читанням CSV.
- `OutputStrategy` визначає спільний інтерфейс `write()`.
- `ConsoleOutputStrategy`, `FileOutputStrategy`, `RedisOutputStrategy`, `KafkaOutputStrategy` реалізують різні способи запису.
- `OutputStrategyFactory` створює потрібну стратегію на основі конфігурації.
- У `main.py` логіка читання даних **не залежить** від того, куди вони будуть записані.

## 6. Важливо для захисту
Якщо Redis або Kafka не запущені, програма не падає з нечитабельним traceback'ом бібліотеки, а викидає зрозуміле повідомлення про те, який сервіс потрібно підняти.

## 7. Швидкий сценарій для демонстрації викладачу
1. `python main.py --download`
2. `docker compose up -d`
3. Поставити `strategy: "console"` і запустити `python main.py`
4. Поставити `strategy: "file"` і запустити `python main.py`
5. Поставити `strategy: "redis"` і запустити `python main.py`
6. Виконати `python scripts/check_redis.py`
7. Поставити `strategy: "kafka"` і запустити `python main.py`
8. Виконати `python scripts/check_kafka.py`

