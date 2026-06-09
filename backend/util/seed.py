# backend\util\seed.py

import random

from backend.blockchain.blockchain import Blockchain
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.wallet.transaction_pool import TransactionPool


def seed_blockchain_data(
    blockchain: Blockchain, transaction_pool: TransactionPool
) -> None:

    total_blocks = random.randint(15, 20)

    for _ in range(total_blocks):

        tx_list = []
        tx_in_block = random.randint(1, 3)
        for _ in range(tx_in_block):
            sender_wallet = Wallet()
            recipient_wallet = Wallet()
            amount = random.randint(3, 50)
            tx = Transaction(
                sender_wallet=sender_wallet,
                recipient_address=recipient_wallet.address,
                amount=amount,
            )
            tx_list.append(tx.to_json())

        blockchain.add_block(tx_list)
    tx_in_pool = random.randint(3, 5)
    for _ in range(tx_in_pool):
        sender_wallet = Wallet()
        recipient_wallet = Wallet()
        amount = random.randint(3, 50)
        tx = Transaction(
            sender_wallet=sender_wallet,
            recipient_address=recipient_wallet.address,
            amount=amount,
        )
        transaction_pool.set_transaction(tx=tx)
