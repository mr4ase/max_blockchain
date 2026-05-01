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

        block_data = transaction_pool.transaction_data()
        blockchain.add_block(block_data)

        block = blockchain.chain[-1]
        pubsub.broadcast_block(block=block)

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
