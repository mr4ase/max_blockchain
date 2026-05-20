# backend\wallet\wallet.py

from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

from typing import Any, TYPE_CHECKING
from backend.config import STARTING_BALANCE
from backend.util.encoding_utils import encode_data_to_bytes
if TYPE_CHECKING:
    from backend.blockchain.blockchain import Blockchain


class Wallet:
    def __init__(self, blockchain: Blockchain | None = None) -> None:
        self._private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        self.public_key = self._private_key.public_key()
        self.blockchain = blockchain

        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        public_key_hash = hashes.Hash(hashes.SHA256())
        public_key_hash.update(public_key_bytes)
        public_key_result = public_key_hash.finalize()

        self.address = public_key_result.hex()

    def sign(self, data: Any) -> bytes:
        data_in_bytes = encode_data_to_bytes(data=data)
        signature = self._private_key.sign(data_in_bytes, ec.ECDSA(hashes.SHA256()))
        return signature

    def public_key_str(self) -> str:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    @property
    def balance(self):
        return self.calculate_balance(self.blockchain, self.address)

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

    @staticmethod
    def calculate_balance(blockchain: Blockchain | None, address: str) -> int:

        balance = STARTING_BALANCE

        if not blockchain:
            return balance

        for block in blockchain.chain:
            for transaction in block.data:
                if transaction["input"]["address"] == address:
                    balance = transaction["output"][address]
                elif address in transaction["output"]:
                    balance += transaction["output"][address]

        return balance
