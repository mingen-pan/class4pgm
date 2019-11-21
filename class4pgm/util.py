import random
import string


def quote_string(v):
    """
    Copy from RedisGraph
    quote_string wraps given v with quotes incase
    v is a string.
    """
    if not isinstance(v, str):
        return v
    if len(v) == 0:
        return '""'

    if v[0] != '"':
        v = '"' + v

    if v[-1] != '"':
        v = v + '"'

    return v


def random_string(length=10):
    """
    Returns a random N chracter long string.
    """
    return ''.join(random.choice(string.ascii_lowercase) for x in range(length))