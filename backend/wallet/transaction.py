# backend\wallet\transaction.py

import time
from uuid import uuid4
from backend.wallet.wallet import Wallet


class Transaction:
    def __init__(
        self, sender_wallet: Wallet, recipient_address: str, amount: int
    ) -> None:

        if amount > sender_wallet.balance:
            raise Exception(
                f"The amount {amount} to send is more than there is on a balance"
            )

        self.id = str(uuid4())[0:8]

        self.output = self._create_output(
            sender_wallet,
            recipient_address=recipient_address,
            amount=amount,
        )

        self.input = self._create_input(sender_wallet=sender_wallet, output=self.output)

    def update(
        self, sender_wallet: Wallet, recipient_address: str, amount: int
    ) -> None:

        if recipient_address == sender_wallet.address:
            raise Exception("The sender and recipient have the same addresses!")

        if amount > self.output[sender_wallet.address]:
            raise Exception("The amount exceeds the current balance!")

        if recipient_address not in self.output:
            self.output[recipient_address] = amount
        else:
            self.output[recipient_address] += amount
        self.output[sender_wallet.address] -= amount

        self.input = self._create_input(sender_wallet=sender_wallet, output=self.output)

    def _create_output(
        self,
        sender_wallet: Wallet,
        recipient_address: str,
        amount: int,
    ) -> dict:
        return {
            recipient_address: amount,
            sender_wallet.address: sender_wallet.balance - amount,
        }

    def _create_input(self, sender_wallet: Wallet, output: dict) -> dict:
        return {
            "timestamp": time.time_ns(),
            "amount": sender_wallet.balance,
            "address": sender_wallet.address,
            "public_key": sender_wallet.public_key,
            "signature": sender_wallet.sign(output),
        }
