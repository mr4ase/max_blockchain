# backend\util\crypto_hash.py

import hashlib
import json
from backend.util.encoding_utils import encode_data_to_bytes


def crypto_hash(*args):
    """
    Return a sha-256 hash of the given arguments.
    """
    sorted_bytes_args = sorted(map(lambda data: encode_data_to_bytes(data), args))
    sorted_byte_data = b"".join(sorted_bytes_args)

    return hashlib.sha256(sorted_byte_data).hexdigest()


def main():
    print(f"crypto_hash('one', 2, [3]): {crypto_hash('one', 2, [3])}")
    print(f"crypto_hash(2, 'one', [3]): {crypto_hash(2, 'one', [3])}")


if __name__ == "__main__":
    main()
