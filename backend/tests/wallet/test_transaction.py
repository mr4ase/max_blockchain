# backend\tests\wallet\test_transaction.py

from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.config import STARTING_BALANCE
import pytest


def test_tx_init_happy_path(sender_wallet, recipient_wallet):

    test_amount = 100

    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)

    assert isinstance(tx.id, str)
    assert len(tx.id) == 8
    assert tx.output.get(recipient_wallet.address) == test_amount
    assert tx.output.get(sender_wallet.address) == sender_wallet.balance - test_amount
    assert tx.input.get("amount") == sender_wallet.balance
    assert tx.input.get("address") == sender_wallet.address
    assert tx.input.get("public_key") == sender_wallet.public_key
    assert sender_wallet.verify(
        tx.input["public_key"], tx.output, tx.input["signature"]
    )


def test_tx_amount_is_over_balance(sender_wallet, recipient_wallet):

    test_amount = 2000

    with pytest.raises(
        Exception,
        match=f"The amount {test_amount} to send is more than there is on a balance",
    ):
        tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)


def test_tx_wrong_signature(sender_wallet, recipient_wallet):

    test_amount = 100
    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)

    right_signature = tx.input["signature"]
    corrupted = bytearray(right_signature)
    corrupted[0] ^= 1
    corrupted_signature = bytes(corrupted)

    assert not sender_wallet.verify(
        sender_wallet.public_key, tx.output, corrupted_signature
    )


def test_tx_wrong_output(sender_wallet, recipient_wallet):
    test_amount = 100

    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)

    corrupted_output = {
        recipient_wallet.address: 300,
        sender_wallet.address: sender_wallet.balance - test_amount,
    }

    tx.output = corrupted_output

    assert not sender_wallet.verify(
        sender_wallet.public_key, tx.output, tx.input["signature"]
    )


def test_tx_output_sum_always_equal_balance(sender_wallet, recipient_wallet):
    test_amount = 100

    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)

    assert sum(tx.output.values()) == sender_wallet.balance


def test_update_tx_happy_path(sender_wallet, recipient_wallet):
    test_amount = 100
    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)
    balance_after_first_tx = tx.output[sender_wallet.address]
    test_amount_for_update = 200
    tx.update(
        sender_wallet=sender_wallet,
        recipient_address=recipient_wallet.address,
        amount=test_amount_for_update,
    )
    new_sender_balance = balance_after_first_tx - test_amount_for_update
    assert tx.output[sender_wallet.address] == new_sender_balance
    assert tx.output[recipient_wallet.address] == test_amount + test_amount_for_update
    assert sender_wallet.verify(
        public_key=sender_wallet.public_key,
        data=tx.output,
        signature=tx.input["signature"],
    )


def test_update_tx_recipient_sender_are_the_same(sender_wallet, recipient_wallet):
    test_amount = 100
    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)
    test_amount_for_update = 200
    with pytest.raises(
        Exception, match="The sender and recipient have the same addresses!"
    ):
        tx.update(
            sender_wallet=sender_wallet,
            recipient_address=sender_wallet.address,
            amount=test_amount_for_update,
        )


def test_update_tx_amount_exceeds_balance(sender_wallet, recipient_wallet):
    test_amount = 100
    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)
    test_amount_for_update = 2000
    with pytest.raises(Exception, match="The amount exceeds the current balance!"):
        tx.update(
            sender_wallet=sender_wallet,
            recipient_address=recipient_wallet.address,
            amount=test_amount_for_update,
        )
