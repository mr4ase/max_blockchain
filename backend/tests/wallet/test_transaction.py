# backend\tests\wallet\test_transaction.py

from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.config import STARTING_BALANCE
import pytest

def test_tx_init_happy_path():
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    test_amount = 100
    
    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)
    
    assert isinstance(tx.id, str)
    assert len(tx.id) == 8
    assert tx.output.get(recipient_wallet.address) == test_amount
    assert tx.output.get(sender_wallet.address) == sender_wallet.balance - test_amount
    assert tx.input.get("amount") == sender_wallet.balance
    assert tx.input.get("address") == sender_wallet.address
    assert tx.input.get("public_key") == sender_wallet.public_key
    assert sender_wallet.verify(sender_wallet.public_key, tx.output, tx.input["signature"])
    
def test_tx_amount_is_over_balance():
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    test_amount = 2000
    
    with pytest.raises(Exception, match=f"The amount {test_amount} to send is more than there is on a balance"):
        tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)
        
def test_tx_wrong_signature():
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    test_amount = 100
    
    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)
    
    right_signature = tx.input["signature"]
    corrupted = bytearray(right_signature)
    corrupted[0] ^= 1
    corrupted_signature = bytes(corrupted)
    
    assert not sender_wallet.verify(sender_wallet.public_key, tx.output, corrupted_signature)
    
def test_tx_wrong_output():
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    test_amount = 100
    
    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)
    
    corrupted_output = {
        recipient_wallet.address: 300,
        sender_wallet.address: sender_wallet.balance - test_amount
    }
    
    tx.output = corrupted_output
    
    assert not sender_wallet.verify(sender_wallet.public_key, tx.output, tx.input["signature"])
    
def test_tx_output_sum_always_equal_balance():
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    test_amount = 100
    
    tx = Transaction(sender_wallet, recipient_wallet.address, test_amount)
    
    assert sum(tx.output.values()) == sender_wallet.balance