# backend\tests\wallet\test_wallet.py

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from backend.wallet.wallet import Wallet

from typing import Any
import json
from backend.config import STARTING_BALANCE
from backend.util.encoding_utils import encode_data_to_bytes


def test_sign_happy_path():
    wallet = Wallet()
    data_to_sign = "data to sign"
    signature = wallet.sign(data=data_to_sign)
    assert isinstance(signature, bytes)
    assert Wallet.verify(wallet.public_key, data_to_sign, signature)


def test_sign_and_verify_bad_path_corrupted_public_key():
    wallet1 = Wallet()
    wallet2 = Wallet()
    data_to_sign = "data to sign"
    signature = wallet1.sign(data_to_sign)
    assert not Wallet.verify(wallet2.public_key, data_to_sign, signature)


def test_sign_and_verify_bad_path_corrupted_data():
    wallet = Wallet()
    data_to_sign1 = "data to sign"
    signature = wallet.sign(data_to_sign1)
    data_to_sign2 = "corrupted data"
    assert not Wallet.verify(wallet.public_key, data_to_sign2, signature)


def test_sign_and_verify_bad_path_signature_for_different_data():
    wallet = Wallet()
    data_to_sign = "data to sign"
    signature1 = wallet.sign(data_to_sign)
    data_to_sign2 = "new data for signature"
    signature2 = wallet.sign(data_to_sign2)
    assert Wallet.verify(wallet.public_key, data_to_sign, signature1)
    assert not Wallet.verify(wallet.public_key, data_to_sign, signature2)


def test_sign_and_verify_bad_path_wrong_signature():
    wallet = Wallet()
    data_to_sign = "data to sign"
    right_signature = wallet.sign(data_to_sign)
    corrupted = bytearray(right_signature)
    corrupted[0] ^= 1
    corrupted_signature = bytes(corrupted)
    assert Wallet.verify(wallet.public_key, data_to_sign, right_signature)
    assert not Wallet.verify(wallet.public_key, data_to_sign, corrupted_signature)
