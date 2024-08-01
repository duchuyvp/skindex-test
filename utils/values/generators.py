import random
import string


def generate_random_string(
    length: int = 8,
    upper_case: bool = False,
    numeric: bool = False,
    special_symbols: bool = False,
) -> str:
    """generate a random string with the given length and charactors"""

    charactors = string.ascii_lowercase
    if upper_case:
        charactors += string.ascii_uppercase
    if numeric:
        charactors += string.digits
    if special_symbols:
        charactors += string.punctuation

    return "".join(random.choice(charactors) for _ in range(length))
