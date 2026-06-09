# backend\app\routes.py

from flask import jsonify, current_app, request
from pydantic import ValidationError
from backend.app.schemas import TransactionCreateSchema
from backend.wallet.transaction import Transaction


def register_routes(app):

    @app.route("/test", methods=["GET"])
    def test():
        return "Test"

    @app.route("/", methods=["GET"])
    def route_default():
        return "Welcome to Blockchain!"

    @app.route("/blockchain", methods=["GET"])
    def route_blockchain():
        blockchain = current_app.config["blockchain"]
        return jsonify(blockchain.to_json())

    @app.route("/blockchain/mine", methods=["GET"])
    def mine_blockchain_block():
        blockchain = current_app.config["blockchain"]
        pubsub = current_app.config["pubsub"]
        transaction_pool = current_app.config["transaction_pool"]
        wallet = current_app.config["wallet"]

        block_data = transaction_pool.transaction_data()
        reward_tx = Transaction.reward_transaction(wallet)
        block_data.append(reward_tx.to_json())
        blockchain.add_block(block_data)

        block = blockchain.chain[-1]
        pubsub.broadcast_block(block=block)
        transaction_pool.clear_blockchain_transactions(blockchain)

        return jsonify(block.to_json())

    @app.route("/blockchain/transaction", methods=["POST"])
    def create_transaction():
        data = request.get_json()

        if data is None:
            return jsonify({"error": "Payload must be a valid JSON"}), 400

        try:
            valid_data = TransactionCreateSchema(**data)

        except ValidationError as e:
            return jsonify({"error": "Invalid data", "details": e.errors()}), 400

        wallet = current_app.config["wallet"]
        pubsub = current_app.config["pubsub"]
        transaction_pool = current_app.config["transaction_pool"]
        new_tx = transaction_pool.existing_transaction(wallet.address)

        try:
            if new_tx:
                new_tx.update(wallet, valid_data.recipient_address, valid_data.amount)
                response_code = 200
            else:
                new_tx = Transaction(
                    wallet, valid_data.recipient_address, valid_data.amount
                )
                response_code = 201
        except Exception as e:
            return (
                jsonify({"error": "Invalid transaction data", "details": str(e)}),
                400,
            )
        transaction_pool.set_transaction(new_tx)
        pubsub.broadcast_transaction(tx=new_tx)

        return (
            jsonify(new_tx.to_json()),
            response_code,
        )

    @app.route("/wallet/info", methods=["GET"])
    def wallet_info():
        wallet = current_app.config["wallet"]

        return jsonify({"address": wallet.address, "balance": wallet.balance})

    @app.route("/blockchain/range", methods=["GET"])
    def blockchain_range():
        start = request.args.get("start")
        end = request.args.get("end")

        if start is None:
            return jsonify({"error": "Start parameter missed"}), 400

        try:
            start_index = int(start)
        except ValueError as e:
            return jsonify({"error": "Start parameter type error. Must be int"}), 400

        if start_index < 0:
            return jsonify({"error": "Start parameter must be non-negative."}), 400

        if end is None:
            return jsonify({"error": "End parameter missed"}), 400
        try:
            end_index = int(end)
        except ValueError as e:
            return jsonify({"error": "End parameter type error. Must be int"}), 400

        blockchain = current_app.config["blockchain"]
        chain_len = len(blockchain.chain)
        block_range = []

        if start_index >= chain_len:
            return jsonify([]), 200

        if end_index < 0:
            return jsonify({"error": "End parameter must be non-negative."}), 400

        if end_index < start_index:
            return (
                jsonify({"error": "End parameter must greater or equal than start"}),
                400,
            )

        if end_index >= chain_len:
            end_index = chain_len

        for i in range(chain_len - 1 - start_index, chain_len - 1 - end_index, -1):
            block_range.append(blockchain.chain[i].to_json())

        return jsonify(block_range), 200

    @app.route("/blockchain/length", methods=["GET"])
    def blockchain_length():
        blockchain = current_app.config["blockchain"]
        return jsonify(len(blockchain.chain)), 200

    @app.route("/known-addresses", methods=["GET"])
    def blockchain_known_addresses():
        unique_addresses = set()
        blockchain = current_app.config["blockchain"]
        for block in blockchain.chain:
            for transaction in block.data:
                unique_addresses.update(transaction["output"].keys())

        return jsonify(sorted(unique_addresses)), 200

    @app.route("/transaction-pool", methods = ["GET"])
    def get_transaction_pool():
        transaction_pool = current_app.config["transaction_pool"]
        return jsonify(transaction_pool.transaction_data()), 200