import os

class Shortener:
    def get_url(self, code: str) -> str:
        return f"{os.environ['BASE_URL']}/{code}"