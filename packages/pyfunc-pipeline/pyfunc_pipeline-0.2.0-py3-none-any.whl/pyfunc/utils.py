from typing import Union

def square(x: Union[int, float]) -> Union[int, float]:
    """Return the square of a number."""
    return x * x

def increment(x: Union[int, float]) -> Union[int, float]:
    """Increment a number by 1."""
    return x + 1

def half(x: Union[int, float]) -> Union[int, float]:
    """Return half of a number."""
    return x / 2
