# backend\pubsub.py
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
import uuid
import threading

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-11992c54-cdb5-40b8-aebd-6a4c6c312533"
pnconfig.publish_key = "pub-c-7b59d3ea-64bb-4fd2-a9d3-9220d0e6f60f"
pnconfig.uuid = str(uuid.uuid4())

TEST_CHANNEL = "TEST_CHANNEL"
# LISTENER_IS_CONNECTED = threading.Event()


class Listener(SubscribeCallback):
    def __init__(self, connected_event):
        self.connected_event = connected_event

    def message(self, pubnub, message):
        print(f"\n-- Incoming message: {message.message}")
        # return super().message(pubnub, message)

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            self.connected_event.set()


class PubSub:
    def __init__(self) -> None:
        self.connected = threading.Event()
        self.pubnub = PubNub(pnconfig)
        listener = Listener(self.connected)
        self.pubnub.add_listener(listener)
        self.pubnub.subscribe().channels([TEST_CHANNEL]).execute()
        self.connected.wait(timeout=5)
        if not self.connected.is_set():
            raise RuntimeError("PubNub connection timeout")

    def publish(self, channel: str, message: dict) -> None:
        self.pubnub.publish().channel(channel).message(message).sync()


def main():
    pubsub = PubSub()
    message = {"foo": "bar"}
    print("Publishing message...")
    pubsub.publish(TEST_CHANNEL, message=message)
    print("Message published...")


if __name__ == "__main__":
    main()
