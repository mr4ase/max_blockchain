# backend\tests\wallet\test_transaction_pool.py

from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.wallet.transaction_pool import TransactionPool

def test_transaction_pool_add_tx(recipient_wallet):
    wallet = Wallet()
    transaction_pool = TransactionPool()
    test_amount = 100
    tx = Transaction(wallet, recipient_wallet.address, test_amount)
    transaction_pool.set_transaction(tx)
    
    assert transaction_pool.transaction_map[tx.id] is tx
    
def test_existing_transaction(): #TODO test_existing_transaction
    pass

def test_clear_blockchain_transactions(): #TODO test_existing_transaction
    pass

def test_transaction_data(): #TODO test_existing_transaction
    pass