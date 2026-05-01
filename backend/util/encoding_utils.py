# backend\util\encoding_utils.py

import json
import base64
from typing import Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_public_key


def encode_data_to_bytes(data: Any) -> bytes:
    data_in_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode(
        encoding="utf-8"
    )
    return data_in_bytes


def public_key_to_str(public_key: ec.EllipticCurvePublicKey) -> str:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


def signature_to_str(signature: bytes) -> str:
    return base64.b64encode(signature).decode("utf-8")


def signature_from_str(signature: str) -> bytes:
    return base64.b64decode(signature)


def public_key_from_str(public_key_str: str) -> ec.EllipticCurvePublicKey:
    public_key = load_pem_public_key(public_key_str.encode(encoding="utf-8"))

    if not isinstance(public_key, ec.EllipticCurvePublicKey):
        raise TypeError("Public key is not an elliptic curve public key")

    return public_key
