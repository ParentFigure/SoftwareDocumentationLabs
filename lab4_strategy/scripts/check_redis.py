from __future__ import annotations

import redis

client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
items = client.lrange("violations:list", 0, -1)
print(f"Redis items: {len(items)}")
for item in items[:10]:
    print(item)
