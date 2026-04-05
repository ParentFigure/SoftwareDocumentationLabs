from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable


class OutputStrategy(ABC):
    @abstractmethod
    def write(self, lines: Iterable[str]) -> None:
        raise NotImplementedError


class ConsoleOutputStrategy(OutputStrategy):
    def write(self, lines: Iterable[str]) -> None:
        for line in lines:
            print(line)


class FileOutputStrategy(OutputStrategy):
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)

    def write(self, lines: Iterable[str]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as file:
            for line in lines:
                file.write(line + "\n")


class RedisOutputStrategy(OutputStrategy):
    def __init__(self, host: str, port: int, db: int, list_key: str, clear_before_write: bool) -> None:
        import redis

        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.list_key = list_key
        self.clear_before_write = clear_before_write

    def write(self, lines: Iterable[str]) -> None:
        try:
            self.client.ping()
        except Exception as error:
            raise RuntimeError(
                "Redis is not available at the configured host/port. Start Redis before using strategy=redis."
            ) from error

        if self.clear_before_write:
            self.client.delete(self.list_key)

        for line in lines:
            self.client.rpush(self.list_key, line)


class KafkaOutputStrategy(OutputStrategy):
    def __init__(
        self,
        bootstrap_servers: list[str],
        topic: str,
        client_id: str,
    ) -> None:
        from kafka import KafkaProducer

        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            client_id=client_id,
            value_serializer=lambda value: value.encode("utf-8"),
            request_timeout_ms=10000,
            api_version_auto_timeout_ms=10000,
        )

    def write(self, lines: Iterable[str]) -> None:
        try:
            self.producer.bootstrap_connected()
        except Exception as error:
            raise RuntimeError(
                "Kafka is not available at the configured bootstrap server. Start Kafka before using strategy=kafka."
            ) from error

        futures = []
        for line in lines:
            futures.append(self.producer.send(self.topic, line))

        for future in futures:
            future.get(timeout=10)

        self.producer.flush()
        self.producer.close()
