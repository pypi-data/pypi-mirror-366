import random
import string
from typing import Any, Optional


class Map(dict):
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            return None

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    def items(self):
        return super().items()


def split_string(character: str, value: Optional[str]):
    return list(filter(None, (value or "").split(character)))


def generate_random_string(length=32):
    if not length:
        length = 0

    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))
