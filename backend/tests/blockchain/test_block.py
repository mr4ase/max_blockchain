from backend.blockchain.block import GENESIS_DATA, Block
from backend.config import MINE_RATE, SECONDS
from backend.util.hex_to_binary import hex_to_binary
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
    assert hex_to_binary(block.hash)[:difficulty] == "0" * difficulty


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


def test_is_valid_block_success(last_block, valid_block):
    Block.is_valid_block(last_block, valid_block)
    assert Block.is_valid_block(last_block, valid_block) is None


def test_is_valid_block_bad_last_hash(last_block, valid_block):
    valid_block.last_hash = "broken_last_hash"
    with pytest.raises(Exception, match="The last_hash block is invalid!"):
        Block.is_valid_block(last_block, valid_block)
    # assert valid_block.last_hash != last_block.hash


def test_is_valid_block_proof_of_work_error(last_block, valid_block):
    valid_block.difficulty = 50

    with pytest.raises(Exception, match="The proof of work requirement is not met!"):
        Block.is_valid_block(last_block, valid_block)


def test_is_valid_block_difficulty_difference_jump(last_block, valid_block):
    valid_block.difficulty = last_block.difficulty - 2

    with pytest.raises(Exception, match="The difficulty value is invalid!"):
        Block.is_valid_block(last_block, valid_block)


def test_is_valid_block_hash_is_broken(last_block, valid_block):
    valid_block.data = "new_data_to_break_hash"

    with pytest.raises(Exception, match="The hash of the block is broken!"):
        Block.is_valid_block(last_block, valid_block)
