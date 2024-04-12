import os


class Shortener:
    """
    Class to get the shortened URL.
    """

    def get_url(self, code: str) -> str:
        return f"{os.environ['BASE_URL']}/{code}"
