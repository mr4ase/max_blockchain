# backend\pubsub.py
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
import uuid

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-11992c54-cdb5-40b8-aebd-6a4c6c312533"
pnconfig.publish_key = "pub-c-7b59d3ea-64bb-4fd2-a9d3-9220d0e6f60f"
pnconfig.uuid = str(uuid.uuid4())
pubnub = PubNub(pnconfig)

TEST_CHANNEL = "TEST_CHANNEL"


class Listener(SubscribeCallback):
    def message(self, pubnub, message):
        print(f"\n-- Incoming message: {message}")
        # return super().message(pubnub, message)


pubnub.add_listener(Listener())
print("Listener added")

print("Subscribing...")
pubnub.subscribe().channels([TEST_CHANNEL]).execute()


def main():
    print("Publishing message...")
    pubnub.publish().channel(TEST_CHANNEL).message({"foo": "bar"}).sync()
    print("Message published...")



if __name__ == "__main__":
    main()
