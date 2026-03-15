# backend\app\__init__.py

from flask import Flask

from backend.blockchain.blockchain import Blockchain
from backend.pubsub import PubSub


def create_app():
    app = Flask(__name__)

    blockchain = Blockchain()
    pubsub = PubSub(blockchain=blockchain)

    # временно оставляем тестовые блоки
    # for i in range(3):
    #     blockchain.add_block(i)

    # сохраняем зависимости внутри app
    app.config["blockchain"] = blockchain
    app.config["pubsub"] = pubsub

    from backend.app.routes import register_routes

    register_routes(app)

    return app


# import os
# import random

# from flask import Flask, jsonify
# from backend.blockchain.blockchain import Blockchain
# from backend.pubsub import PubSub


# PORT = 5000

# app = Flask(__name__)
# blockchain = Blockchain()
# pubsub = PubSub(blockchain=blockchain)

# for i in range(3):
#     blockchain.add_block(i)


# @app.route("/test")
# def test():
#     return "Test"


# @app.route("/")
# def route_default():
#     return "Welcome to Blockchain!"


# @app.route("/blockchain", methods=["GET"])
# def route_blockchain():
#     return jsonify(blockchain.to_json())


# @app.route("/blockchain/mine")
# def mine_blockchain_block():
#     block_data = "new_block_data"
#     blockchain.add_block(block_data)

#     block = blockchain.chain[-1]
#     pubsub.broadcast_block(block=block)

#     return jsonify(block.to_json())


# # if os.environ.get("PEER") == "True":
# #     PORT = random.randint(5001, 6000)
# PORT = int(os.environ.get("PORT", 5000))
# app.run(port=PORT)
