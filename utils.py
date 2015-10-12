import hashlib

from datetime import datetime, timezone


def now_utc():
    return datetime.now(timezone.utc)


def get_hash(password, salt):
    m = hashlib.sha512()
    m.update(salt.encode('utf8'))
    m.update(password.encode('utf8'))
    return m.digest()
