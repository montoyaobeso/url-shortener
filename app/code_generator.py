import random
from app.constants import ALPHABET, CODE_LENGHT


class CodeGenerator:
    """
    Class to generate random codes.
    """

    def get_code(self):
        return "".join(random.choices(ALPHABET, k=CODE_LENGHT))
