# backend\app\__init__.py

from flask import Flask

from backend.blockchain.blockchain import Blockchain
from backend.pubsub import PubSub
from backend.wallet.wallet import Wallet
from backend.wallet.transaction_pool import TransactionPool


def create_app():
    app = Flask(__name__)

    blockchain = Blockchain()
    transaction_pool = TransactionPool()
    pubsub = PubSub(blockchain=blockchain, transaction_pool=transaction_pool)
    wallet = Wallet()

    app.config["blockchain"] = blockchain
    app.config["pubsub"] = pubsub
    app.config["wallet"] = wallet
    app.config["transaction_pool"] = transaction_pool

    from backend.app.routes import register_routes

    register_routes(app)

    return app
