"""Creates a flowchart using the Flow library and sends it via Redis."""

import redis
import os
import json


class RedisSender:
    def __init__(self, redis_url=None, channel=None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.channel = channel or os.getenv("REDIS_CHANNEL", "mermaid:latest")
        self.client = redis.Redis.from_url(self.redis_url)

    def send(self, content: str, diagram_type: str = "flowchart"):
        message = json.dumps({"type": diagram_type, "content": content})
        self.client.publish(self.channel, message)
        print(f"✅ Sent diagram to Redis channel '{self.channel}'")
