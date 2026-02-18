from backend.blockchain.block import GENESIS_DATA, Block
from backend.config import MINE_RATE, SECONDS
import pytest
import time


def test_mine_block():
    genesis = Block.genesis()
    data = "test-data"
    block = Block.mine_block(genesis, data)
    difficulty = block.difficulty
    assert isinstance(block, Block)
    assert block.last_hash == genesis.hash
    assert block.data == data
    assert block.hash[:difficulty] == "0" * difficulty


def test_genesis_type():
    genesis = Block.genesis()
    assert isinstance(genesis, Block)


@pytest.mark.parametrize("key, value", GENESIS_DATA.items())
def test_genesis_data(key, value):
    genesis = Block.genesis()
    assert getattr(genesis, key) == value


def test_quickly_mined_block():
    genesis = Block.genesis()
    last_block = Block.mine_block(genesis, "pararam")
    mined_block = Block.mine_block(last_block, "test_pararam")
    # the block is mined very quickly

    assert mined_block.difficulty == last_block.difficulty + 1


def test_slowly_mined_block():
    genesis = Block.genesis()
    last_block = Block.mine_block(genesis, "pararam")
    time.sleep(MINE_RATE / SECONDS)
    mined_block = Block.mine_block(last_block, "test_pararam")

    assert mined_block.difficulty == last_block.difficulty - 1


def test_difficulty_always_above_zero():
    last_block = Block(
        timestamp=time.time_ns(),
        last_hash="test_last_hash",
        hash="test_hash",
        data="test_data",
        difficulty=1,
        nonce=0,
    )
    time.sleep(MINE_RATE / SECONDS)
    mined_block = Block.mine_block(last_block, "test_pararam")

    assert mined_block.difficulty == 1
