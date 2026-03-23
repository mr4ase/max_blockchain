# backend\pubsub.py

from __future__ import annotations

import uuid
import threading
import requests


from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory

from backend.blockchain.block import Block
from backend.blockchain.blockchain import Blockchain


pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-11992c54-cdb5-40b8-aebd-6a4c6c312533"
pnconfig.publish_key = "pub-c-7b59d3ea-64bb-4fd2-a9d3-9220d0e6f60f"
pnconfig.uuid = str(uuid.uuid4())

KNOWN_PEERS = [
    "http://localhost:5000",
    "http://localhost:5001",
    "http://localhost:5002",
    "http://localhost:5003",
]

CHANNELS = {
    "BLOCK_CHANNEL": "BLOCK_CHANNEL",
    "TEST_CHANNEL": "TEST_CHANNEL",
    "TRANSACTION_CHANNEL": "TRANSACTION CHANNEL",
}


class Listener(SubscribeCallback):
    def __init__(self, connected_event, blockchain: Blockchain, pubsub: PubSub):
        self.connected_event = connected_event
        self.blockchain = blockchain
        self.pubsub = pubsub

    def message(self, pubnub, message):
        print(f"\n-- Channel: {message.channel} | Incoming message: {message.message}")

        if message.channel == CHANNELS["BLOCK_CHANNEL"]:
            block = Block.from_json(message.message)
            self.blockchain.handle_block_from_peer(
                block, self.pubsub.resolve_conflicts_with_new_mined_block_callback
            )

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            self.connected_event.set()


class PubSub:
    def __init__(self, blockchain: Blockchain) -> None:
        self.connected = threading.Event()
        self.pubnub = PubNub(pnconfig)
        self.blockchain = blockchain
        self.peers = set(KNOWN_PEERS)
        listener = Listener(self.connected, self.blockchain, self)
        self.pubnub.add_listener(listener)
        self.pubnub.subscribe().channels(CHANNELS.values()).execute()
        self.connected.wait(timeout=5)
        if not self.connected.is_set():
            raise RuntimeError("PubNub connection timeout")

    def publish(self, channel: str, message: dict) -> None:
        self.pubnub.publish().channel(channel).message(message).sync()

    def broadcast_block(self, block: Block):
        self.publish(channel=CHANNELS["BLOCK_CHANNEL"], message=block.to_json())

    def resolve_conflicts_with_new_mined_block_callback(self):

        max_length = len(self.blockchain.chain)
        chain_for_replacing = None

        for peer in self.peers:
            url_handle = f"{peer}/blockchain"
            try:
                response = requests.get(url=url_handle, timeout=3)
            except Exception:
                continue
            if response.status_code != 200:
                continue

            try:
                blockchain_from_peer_json = response.json()
            except Exception:
                continue
            blockchain_from_peer = Blockchain.from_json(
                blockchain_from_json=blockchain_from_peer_json
            )
            length_blockchain_from_peer = len(blockchain_from_peer.chain)
            if length_blockchain_from_peer <= max_length:
                continue

            try:
                Blockchain.is_valid_blockchain(blockchain_from_peer.chain)
            except Exception:
                continue
            max_length = length_blockchain_from_peer
            chain_for_replacing = blockchain_from_peer.chain

        if chain_for_replacing:
            self.blockchain.replace_chain(chain_for_replacing)


def main():
    blockchain = Blockchain()
    pubsub = PubSub(blockchain=blockchain)
    message = {"foo": "bar"}
    print("Publishing message...")
    pubsub.publish(CHANNELS["TEST_CHANNEL"], message=message)
    print("Message published...")


if __name__ == "__main__":
    main()
