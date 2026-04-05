from __future__ import annotations

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "violations-topic",
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    consumer_timeout_ms=5000,
)

count = 0
for message in consumer:
    print(message.value.decode("utf-8"))
    count += 1

print(f"Kafka messages read: {count}")
consumer.close()
