# backend\tests\blockchain\test_blockchain.py
from backend.blockchain.blockchain import Blockchain
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
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


def test_blockchain_replace_chain_shorter_one(blockchain_3_blocks):
    blockchain = Blockchain()

    with pytest.raises(
        Exception, match="Cannot replace the chain. Its lenght is too short"
    ):
        blockchain_3_blocks.replace_chain(blockchain.chain)


def test_blockchain_replace_chain_bad_chain(blockchain_3_blocks):
    blockchain = Blockchain()
    blockchain_3_blocks.chain[-1].data = "corrupted_data"

    with pytest.raises(Exception, match="Cannot replace the chain. It is invalid:"):
        blockchain.replace_chain(blockchain_3_blocks.chain)


# 1. нормальная цепочка с транзакциями - валидная
def test_blockchain_is_valid_tx_chain():
    blockchain = Blockchain()
    sender_wallet = Wallet(blockchain=blockchain)
    sender_wallet2 = Wallet(blockchain=blockchain)
    recipient_wallet = Wallet(blockchain=blockchain)
    test_amount = 200

    tx1 = Transaction(
        sender_wallet=sender_wallet,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )
    tx2 = Transaction(
        sender_wallet=sender_wallet2,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )

    blockchain.add_block([tx1.to_json(), tx2.to_json()])

    tx3 = Transaction(
        sender_wallet=recipient_wallet,
        recipient_address=sender_wallet.address,
        amount=test_amount,
    )

    blockchain.add_block([tx3.to_json()])

    Blockchain.is_valid_transaction_chain(blockchain.chain)

    # 2. проверка на дубликат транзакции


def test_blockchain_is_valid_tx_chain_duplicates():
    blockchain = Blockchain()

    sender_wallet = Wallet()
    sender_wallet2 = Wallet()
    recipient_wallet = Wallet()
    test_amount = 200

    tx1 = Transaction(
        sender_wallet=sender_wallet,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )
    tx2 = Transaction(
        sender_wallet=sender_wallet2,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )
    blockchain.add_block([tx1.to_json(), tx2.to_json()])
    blockchain.add_block([tx1.to_json()])

    with pytest.raises(Exception, match=f"Transaction with id={tx1.id} is duplicated!"):
        Blockchain.is_valid_transaction_chain(blockchain.chain)


# 3. проверка на наличие двух reward tx
def test_blockchain_is_valid_tx_chain_duplicates_rewards_txs():
    blockchain = Blockchain()

    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    miner_wallet = Wallet()
    miner_wallet2 = Wallet()
    test_amount = 200

    tx1 = Transaction(
        sender_wallet=sender_wallet,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )
    tx2 = Transaction.reward_transaction(miner_wallet=miner_wallet)
    tx3 = Transaction.reward_transaction(miner_wallet=miner_wallet2)
    blockchain.add_block([tx1.to_json()])
    blockchain.add_block([tx2.to_json(), tx3.to_json()])

    with pytest.raises(
        Exception,
        match=f"The block with hash={blockchain.chain[-1].hash} already has a reward!",
    ):
        Blockchain.is_valid_transaction_chain(blockchain.chain)


# 4. проверка транзакции на валидность в целом
def test_blockchain_is_valid_tx_chain_tx_is_valid():
    blockchain = Blockchain()
    sender_wallet = Wallet()
    sender_wallet2 = Wallet()
    recipient_wallet = Wallet()
    test_amount = 200

    tx1 = Transaction(
        sender_wallet=sender_wallet,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )
    tx2 = Transaction(
        sender_wallet=sender_wallet2,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )
    tx3 = Transaction(
        sender_wallet=recipient_wallet,
        recipient_address=sender_wallet.address,
        amount=test_amount,
    )
    right_signature = tx2.input["signature"]
    corrupted = bytearray(right_signature)
    corrupted[0] ^= 1
    corrupted_signature = bytes(corrupted)
    tx2.input["signature"] = corrupted_signature

    blockchain.add_block([tx1.to_json(), tx2.to_json()])
    blockchain.add_block([tx3.to_json()])

    with pytest.raises(
        Exception, match=f"Invalid transaction {tx2.id}: The signature is invalid."
    ):
        Blockchain.is_valid_transaction_chain(blockchain.chain)


def test_blockchain_is_valid_transaction_bad_wallet_balance():
    blockchain = Blockchain()
    sender_wallet = Wallet(blockchain=blockchain)
    sender_wallet2 = Wallet(blockchain=blockchain)
    recipient_wallet = Wallet(blockchain=blockchain)
    test_amount = 200

    tx1 = Transaction(
        sender_wallet=sender_wallet,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )

    blockchain.add_block([tx1.to_json()])

    tx2 = Transaction(
        sender_wallet=sender_wallet2,
        recipient_address=recipient_wallet.address,
        amount=test_amount,
    )

    blockchain.add_block([tx2.to_json()])

    tx3 = Transaction(
        sender_wallet=recipient_wallet,
        recipient_address=sender_wallet.address,
        amount=test_amount,
    )

    blockchain.add_block([tx3.to_json()])

    bad_test_amount = 1
    tx4 = Transaction(
        sender_wallet=sender_wallet,
        recipient_address=recipient_wallet.address,
        amount=bad_test_amount,
    )

    tx4.output[sender_wallet.address] = 9000
    tx4.input["amount"] = sum(tx4.output.values())
    tx4.input["signature"] = sender_wallet.sign(tx4.output)

    blockchain.add_block([tx4.to_json()])

    with pytest.raises(Exception, match="has an invalid input amount"):
        Blockchain.is_valid_transaction_chain(blockchain.chain)
