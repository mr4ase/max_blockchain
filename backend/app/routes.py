# backend\app\routes.py

from flask import jsonify, current_app


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

        block_data = "new_block_data"
        blockchain.add_block(block_data)

        block = blockchain.chain[-1]
        pubsub.broadcast_block(block=block)

        return jsonify(block.to_json())