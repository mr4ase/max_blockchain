# backend\wallet\transaction_pool.py

from backend.wallet.transaction import Transaction
from backend.blockchain.blockchain import Blockchain

# from backend.blockchain.block import Block


class TransactionPool:

    def __init__(self) -> None:
        self.transaction_map = {}

    def set_transaction(self, tx: Transaction):
        self.transaction_map[tx.id] = tx

    def existing_transaction(self, wallet_address: str) -> Transaction | None:
        for transaction in self.transaction_map.values():
            if transaction.input.get("address") == wallet_address:
                return transaction
        return None

    def clear(self):
        self.transaction_map.clear()

    def set_map(self, transaction_map: dict):
        self.clear()
        self.transaction_map.update(transaction_map)

    def transaction_data(self) -> list[dict]:
        return [tx.to_json() for tx in self.transaction_map.values()]

    def clear_blockchain_transactions(self, blockchain: Blockchain):
        for block in blockchain.chain:
            for transaction in block.data:
                if transaction["id"] in self.transaction_map:
                    del self.transaction_map[transaction["id"]]
