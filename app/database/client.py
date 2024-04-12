import os
import redis


class RedisClient:
    def __init__(self) -> None:
        self.client = redis.Redis(
            host=os.environ["REDIS_HOST"],
            port=os.environ["REDIS_PORT"],
            decode_responses=os.environ["REDIS_DECODE_RESPONSE"],
            socket_keepalive=True,
        )

    def get_client(self):
        """
        Get the client.
        """
        return self.client

    def get_by_id(self, id: str):
        """
        Get data by the ID (code).
        """
        return self.client.hgetall(id)

    def set_by_id(self, id: str, data: dict):
        """
        Save data by the ID (code).
        """
        self.client.hset(id, mapping=data)
