# backend\tests\blockchain\test_blockchain.py
from backend.blockchain.blockchain import Blockchain
from backend.blockchain.block import Block, GENESIS_DATA
import pytest


def test_blockchain_genesis():
    blockchain = Blockchain()
    assert blockchain.chain[-1].hash == GENESIS_DATA["hash"]


def test_blockchain_add_block(blockchain_3_blocks):
    blockchain_3_blocks.add_block("new_block_data")
    assert blockchain_3_blocks.chain[-1].data == "new_block_data"


def test_blockchain_is_valid_chain(blockchain_3_blocks):
    Blockchain.is_valid_blockchain(blockchain_3_blocks.chain)


def test_blockchain_is_valid_chain_bad_genesis(blockchain_3_blocks):
    blockchain_3_blocks.chain[0].data = "corrupted_data"

    with pytest.raises(
        Exception, match="The blockchain must start with valid genesis block!"
    ):
        Blockchain.is_valid_blockchain(blockchain_3_blocks.chain)


def test_blockchain_replace_chain(blockchain_3_blocks):
    blockchain_short = Blockchain()
    blockchain_long = blockchain_3_blocks
    blockchain_short.replace_chain(blockchain_long.chain)
    assert len(blockchain_long.chain) == len(blockchain_short.chain)
    assert blockchain_long.chain[-1] == blockchain_short.chain[-1]
    assert blockchain_short.chain == blockchain_long.chain
    assert Blockchain.is_valid_blockchain(blockchain_short.chain)
    assert blockchain_short.chain is not blockchain_long.chain
