# backend\app\__init__.py

from flask import Flask, jsonify
from backend.blockchain.blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

for i in range(3):
    blockchain.add_block(i)


@app.route("/test")
def test():
    return "Test"


@app.route("/")
def route_default():
    return "Welcome to Blockchain!"


@app.route("/blockchain")
def route_blockchain():
    return jsonify(blockchain.to_json())

@app.route("/blockchain/mine")
def mine_blockchain_block():
    block_data = "new_block_data"
    blockchain.add_block(block_data)
    
    return jsonify(blockchain.chain[-1].to_json())


app.run()
