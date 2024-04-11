import os
import redis


class RedisClient:
    def __init__(self) -> None:
        self.client = redis.Redis(
            host=os.environ["REDIS_HOST"], 
            port=os.environ["REDIS_PORT"],
            decode_responses=os.environ["REDIS_DECODE_RESPONSE"],
            socket_keepalive=True
        )
    
    def get_client(self):
        return self.client
    
    def get_by_id(self, id: str):
        return self.client.hgetall(id)

    def set_by_id(self, id: str, data: dict):
        self.client.hset(id, mapping=data)
