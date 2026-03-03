# backend\tests\blockchain\conftest.py


from backend.blockchain.block import Block
from backend.blockchain.blockchain import Blockchain
from backend.util.crypto_hash import crypto_hash
from backend.util.hex_to_binary import hex_to_binary

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

    for i in range(3):
        blockchain.add_block(i)

    return blockchain
