from __future__ import annotations
from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD_INPUT


class Blockchain:
    """
    Blockchain: a public ledger of transactions.
    Implemented as a list of blocks - data sets of transactions
    """

    def __init__(self):
        self.chain = [Block.genesis()]

    def add_block(self, data):
        self.chain.append(Block.mine_block(self.chain[-1], data))

    def __repr__(self):
        return f"Blockchain: {self.chain}"

    def replace_chain(self, chain):

        if len(chain) <= len(self.chain):
            raise Exception("Cannot replace the chain. Its lenght is too short")

        try:
            Blockchain.is_valid_blockchain(chain)
        except Exception as e:
            raise Exception(f"Cannot replace the chain. It is invalid: {e}")

        self.chain = list(chain)

    def to_json(self):
        serialized_chain = []
        # serialized_chain = [block.to_json() for block in self.chain]
        serialized_chain = list(map(lambda block: block.to_json(), self.chain))
        print(serialized_chain)

        return serialized_chain

    def handle_block_from_peer(
        self, block: Block, resolve_conflicts_with_new_mined_block_callback
    ):
        if any(bl.hash == block.hash for bl in self.chain):
            print("Block already exists in the chain")
            return

        last_block = self.chain[-1]

        try:
            Block.is_valid_block(last_block=last_block, block=block)
            self.chain.append(block)
            print("New block added")
        except Exception as e:
            print(f"Received invalid block: {e}")
            resolve_conflicts_with_new_mined_block_callback()

    @staticmethod
    def from_json(blockchain_from_json: list[dict]):
        if not isinstance(blockchain_from_json, list):
            raise ValueError("Blockchain JSON must be a list!")

        blocks_from_json = [
            Block.from_json(block_json) for block_json in blockchain_from_json
        ]
        blockchain = Blockchain()
        blockchain.chain = blocks_from_json
        return blockchain

    @staticmethod
    def is_valid_blockchain(chain) -> bool:
        """
        Validate the whole chain.
        - start with genesis
        - blocks must be formatted correctly

        """
        if chain[0] != Block.genesis():
            raise Exception("The blockchain must start with valid genesis block!")

        for i in range(1, len(chain)):
            block = chain[i]
            last_block = chain[i - 1]
            Block.is_valid_block(last_block=last_block, block=block)

        return True

    @staticmethod
    def is_valid_transaction_chain(chain: list) -> None:

        tx_unique_id_set = set()
        for i in range(len(chain)):
            block = chain[i]

            is_rewarded = False

            for transaction_json in block.data:
                transaction = Transaction.from_json(transaction_json)

                if transaction.id in tx_unique_id_set:
                    raise Exception(
                        f"Transaction with id={transaction.id} is duplicated!"
                    )
                tx_unique_id_set.add(transaction.id)

                if transaction.input == MINING_REWARD_INPUT:
                    if is_rewarded:
                        raise Exception(
                            f"The block with hash={block.hash} already has a reward!"
                        )
                    is_rewarded = True
                else:
                    historic_blockchain = Blockchain()
                    historic_blockchain.chain = chain[:i]

                    historic_balance = Wallet.calculate_balance(
                        blockchain=historic_blockchain,
                        address=transaction.input["address"],
                    )
                    if historic_balance != transaction.input["amount"]:
                        raise Exception(
                            f"Transaction with id={transaction.id} has an invalid input amount!"
                        )

                Transaction.is_valid(transaction)


def main():
    blockchain = Blockchain()
    blockchain.add_block("one")
    blockchain.add_block("two")

    print(blockchain)
    print(f"blockchain.py __name__: {__name__}")


if __name__ == "__main__":
    main()
