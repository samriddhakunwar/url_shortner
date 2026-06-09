"""
Base62 encoding utilities for generating short URL codes.

Uses a deterministic Base62 encoding of a counter (backed by the DB primary key)
with a random salt fallback for collision safety.
"""

import time

BASE62_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'


def base62_encode(number):
    """Encode a positive integer into a Base62 string.

    Args:
        number: A non-negative integer to encode.

    Returns:
        A Base62-encoded string representation.

    Raises:
        ValueError: If the number is negative.

    Examples:
        >>> base62_encode(0)
        '0'
        >>> base62_encode(61)
        'z'
        >>> base62_encode(62)
        '10'
    """
    if number < 0:
        raise ValueError('number must be non-negative')
    if number == 0:
        return BASE62_ALPHABET[0]

    result = []
    while number > 0:
        number, remainder = divmod(number, 62)
        result.append(BASE62_ALPHABET[remainder])
    return ''.join(reversed(result))


def generate_short_code():
    """Generate a unique short code using Base62 encoding.

    Combines a microsecond timestamp with a counter offset to produce
    unique, short, URL-safe codes. Falls back to a retry loop if a
    collision occurs (extremely unlikely).

    Returns:
        A unique Base62-encoded short code string.
    """
    from shortener.models import ShortURL

    # Use current microsecond timestamp as the seed for Base62 encoding.
    # This produces short, deterministic, non-sequential codes.
    timestamp_us = int(time.time() * 1_000_000)
    code = base62_encode(timestamp_us)

    # Collision check with retry (shift by 1 on each attempt)
    attempt = 0
    while ShortURL.objects.filter(short_code=code).exists():
        attempt += 1
        code = base62_encode(timestamp_us + attempt)

    return code
