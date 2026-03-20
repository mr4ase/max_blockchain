# backend\wallet\wallet.py
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

from typing import Any
import json
from backend.config import STARTING_BALANCE
from backend.util.encoding_utils import encode_data_to_bytes

# TASKS


class Wallet:
    def __init__(self) -> None:
        self._private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        self.public_key = self._private_key.public_key()

        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        public_key_hash = hashes.Hash(hashes.SHA256())
        public_key_hash.update(public_key_bytes)
        public_key_result = public_key_hash.finalize()

        self.address = public_key_result.hex()
        self.balance = STARTING_BALANCE

    def sign(self, data: Any) -> bytes:
        data_in_bytes = encode_data_to_bytes(data=data)
        signature = self._private_key.sign(data_in_bytes, ec.ECDSA(hashes.SHA256()))
        return signature

    @staticmethod
    def verify(
        public_key: ec.EllipticCurvePublicKey, data: Any, signature: bytes
    ) -> bool:

        data_in_bytes = encode_data_to_bytes(data=data)
        try:
            public_key.verify(signature, data_in_bytes, ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False
