# backend\util\encoding_utils.py

import json
from typing import Any


def encode_data_to_bytes(data: Any) -> bytes:
    data_in_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode(
        encoding="utf-8"
    )
    return data_in_bytes
