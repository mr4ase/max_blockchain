# backend\app\__init__.py

from flask import Flask
from flask_cors import CORS
import os

from backend.blockchain.blockchain import Blockchain
from backend.pubsub import PubSub
from backend.wallet.wallet import Wallet
from backend.wallet.transaction_pool import TransactionPool
from backend.util.seed import seed_blockchain_data


def create_app():
    app = Flask(__name__)

    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

    blockchain = Blockchain()
    transaction_pool = TransactionPool()
    pubsub = PubSub(blockchain=blockchain, transaction_pool=transaction_pool)
    wallet = Wallet(blockchain=blockchain)

    seed_data = os.getenv("SEED_DATA", "False")
    if seed_data.lower() == "true":
        seed_blockchain_data(blockchain=blockchain, transaction_pool=transaction_pool)

    app.config["blockchain"] = blockchain
    app.config["pubsub"] = pubsub
    app.config["wallet"] = wallet
    app.config["transaction_pool"] = transaction_pool

    from backend.app.routes import register_routes

    register_routes(app)

    return app
