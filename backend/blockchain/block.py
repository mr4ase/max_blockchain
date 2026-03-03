# backend\blockchain\block.py

from __future__ import annotations


import time

from backend.util.crypto_hash import crypto_hash
from backend.config import MINE_RATE
from backend.util.hex_to_binary import hex_to_binary

GENESIS_DATA = {
    "timestamp": 1,
    "last_hash": "genesis_last_hash",
    "hash": "genesis_hash",
    "data": [],
    "difficulty": 4,
    "nonce": "genesis_nonce",
}


class Block:
    """
    Block: a unit of storage.
    Store transactions in a blockchain that supports a cryptocurrency.
    """

    def __init__(self, timestamp, last_hash, hash, data, difficulty, nonce):
        self.timestamp = timestamp
        self.last_hash = last_hash
        self.hash = hash
        self.data = data
        self.difficulty = difficulty
        self.nonce = nonce

    def __repr__(self):
        return (
            "Block("
            f"timestamp: {self.timestamp}, "
            f"last_hash: {self.last_hash}, "
            f"hash: {self.hash}, "
            f"data: {self.data}), "
            f"difficulty: {self.difficulty}), "
            f"nonce: {self.nonce})"
        )
        
    def __eq__(self, value: object) -> bool:
        return self.__dict__ == value.__dict__

    @staticmethod
    def mine_block(last_block, data):
        """
        Mine a block based on the given last_block and data.
        """
        timestamp = time.time_ns()
        last_hash = last_block.hash
        difficulty = Block.adjust_difficulty(last_block, timestamp)
        nonce = 0
        hash = crypto_hash(timestamp, last_hash, data, difficulty, nonce)

        while hex_to_binary(hash)[:difficulty] != "0" * difficulty:
            timestamp = time.time_ns()
            nonce += 1
            difficulty = Block.adjust_difficulty(last_block, timestamp)

            hash = crypto_hash(timestamp, last_hash, data, difficulty, nonce)

        return Block(timestamp, last_hash, hash, data, difficulty, nonce)

    @staticmethod
    def genesis():
        """
        Generate the genesis block.
        """
        return Block(**GENESIS_DATA)

    @staticmethod
    def adjust_difficulty(last_block, new_timestamp):

        if (new_timestamp - last_block.timestamp) < MINE_RATE:
            return last_block.difficulty + 1

        if (last_block.difficulty - 1) > 0:
            return last_block.difficulty - 1

        return 1

    @staticmethod
    def is_valid_block(last_block: Block, block: Block):

        if block.last_hash != last_block.hash:
            raise Exception("The last_hash block is invalid!")

        if hex_to_binary(block.hash)[: block.difficulty] != "0" * block.difficulty:
            raise Exception("The proof of work requirement is not met!")

        if abs(block.difficulty - last_block.difficulty) > 1:
            raise Exception("The difficulty value is invalid!")

        reconstructed_hash = crypto_hash(
            block.timestamp, block.last_hash, block.data, block.difficulty, block.nonce
        )

        if block.hash != reconstructed_hash:
            raise Exception("The hash of the block is broken!")


def main():
    genesis_block = Block.genesis()
    bad_block = Block.mine_block(genesis_block, "foo")
    # bad_block.last_hash = "bad_last_hash"

    try:
        Block.is_valid_block(genesis_block, bad_block)
    except Exception as e:
        print(f"is_valid_block exception error: {e}")


if __name__ == "__main__":
    main()
