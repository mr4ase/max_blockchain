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
from backend.blockchain.blockchain import Blockchain
from backend.wallet.transaction import Transaction


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


def test_calculate_balance(sender_wallet, recipient_wallet):
    blockchain = Blockchain()

    # wallet never participated in transactions:
    assert (
        Wallet.calculate_balance(address=sender_wallet.address, blockchain=blockchain)
        == STARTING_BALANCE
    )

    test_amount = 100
    tx1 = Transaction(
        sender_wallet=sender_wallet,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )
    blockchain.add_block([tx1.to_json()])

    # sender's wallet balance updated
    assert (
        Wallet.calculate_balance(address=sender_wallet.address, blockchain=blockchain)
        == STARTING_BALANCE - test_amount
    )

    wallet2 = Wallet()
    tx2 = Transaction(
        sender_wallet=wallet2,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )
    blockchain.add_block([tx2.to_json()])

    # recipient's wallet balance updated
    assert (
        Wallet.calculate_balance(
            address=recipient_wallet.address, blockchain=blockchain
        )
    ) == STARTING_BALANCE + test_amount + test_amount
