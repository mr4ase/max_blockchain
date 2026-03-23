# backend\app\__init__.py

from flask import Flask

from backend.blockchain.blockchain import Blockchain
from backend.pubsub import PubSub


def create_app():
    app = Flask(__name__)

    blockchain = Blockchain()
    pubsub = PubSub(blockchain=blockchain)

    app.config["blockchain"] = blockchain
    app.config["pubsub"] = pubsub

    from backend.app.routes import register_routes

    register_routes(app)

    return app
