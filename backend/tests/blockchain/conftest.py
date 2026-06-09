# backend\tests\blockchain\conftest.py


from backend.blockchain.block import Block
from backend.blockchain.blockchain import Blockchain
from backend.util.crypto_hash import crypto_hash
from backend.util.hex_to_binary import hex_to_binary
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction


import time
import pytest


@pytest.fixture
def last_block() -> Block:
    return Block.genesis()


@pytest.fixture
def valid_block(last_block) -> Block:
    return Block.mine_block(last_block=last_block, data="valid_block_data")


@pytest.fixture
def blockchain_3_blocks() -> Blockchain:
    blockchain = Blockchain()
    test_amount = 20

    for _ in range(3):
        sender = Wallet()
        recipient = Wallet()
        tx = Transaction(
            sender_wallet=sender,
            recipient_address=recipient.address,
            amount=test_amount,
        )
        blockchain.add_block([tx.to_json()])

    return blockchain
