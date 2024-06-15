from random import choice
from string import ascii_lowercase, digits


def generate_hash(length: int = 8) -> str:
    """Generate a random string of given length."""
    return "".join(choice(ascii_lowercase + digits) for _ in range(length))
