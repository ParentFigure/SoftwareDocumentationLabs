from __future__ import annotations

from src.output_strategies import (
    ConsoleOutputStrategy,
    FileOutputStrategy,
    KafkaOutputStrategy,
    OutputStrategy,
    RedisOutputStrategy,
)


class OutputStrategyFactory:
    @staticmethod
    def create(output_config: dict) -> OutputStrategy:
        strategy_name = output_config["strategy"].strip().lower()

        if strategy_name == "console":
            return ConsoleOutputStrategy()

        if strategy_name == "file":
            return FileOutputStrategy(output_config["file"]["path"])

        if strategy_name == "redis":
            redis_config = output_config["redis"]
            return RedisOutputStrategy(
                host=redis_config["host"],
                port=int(redis_config["port"]),
                db=int(redis_config.get("db", 0)),
                list_key=redis_config["list_key"],
                clear_before_write=bool(output_config.get("clear_before_write", True)),
            )

        if strategy_name == "kafka":
            kafka_config = output_config["kafka"]
            return KafkaOutputStrategy(
                bootstrap_servers=kafka_config["bootstrap_servers"],
                topic=kafka_config["topic"],
                client_id=kafka_config.get("client_id", "lab4-strategy-producer"),
            )

        raise ValueError(f"Unsupported strategy: {strategy_name}")
