# backend\wallet\transaction.py
from __future__ import annotations

import time
import copy
from uuid import uuid4
from backend.wallet.wallet import Wallet
from backend.util.encoding_utils import (
    public_key_to_str,
    public_key_from_str,
    signature_to_str,
    signature_from_str,
)


class Transaction:
    def __init__(
        self,
        sender_wallet: Wallet | None = None,
        recipient_address: str | None = None,
        amount: int | None = None,
        id: str | None = None,
        input: dict | None = None,
        output: dict | None = None,
    ) -> None:

        self.id = id or str(uuid4())[0:8]

        if input is not None and output is not None:
            self.output = output

            self.input = input

        else:
            if (
                sender_wallet is not None
                and recipient_address is not None
                and amount is not None
            ):
                if amount > sender_wallet.balance:
                    raise Exception(
                        f"The amount {amount} to send is more than there is on a balance"
                    )
                self.output = self._create_output(
                    sender_wallet,
                    recipient_address=recipient_address,
                    amount=amount,
                )

                self.input = self._create_input(
                    sender_wallet=sender_wallet, output=self.output
                )
            else:
                raise Exception(
                    f"Transaction error: sender_wallet/recipient_address/amount is missed"
                )

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

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "input": {
                "timestamp": self.input["timestamp"],
                "amount": self.input["amount"],
                "address": self.input["address"],
                "public_key": public_key_to_str(self.input["public_key"]),
                "signature": signature_to_str(self.input["signature"]),
            },
            "output": self.output,
        }

    @classmethod
    def from_json(cls, tx_json_data: dict) -> Transaction:

        if not isinstance(tx_json_data, dict):
            raise Exception("Error: Invalid JSON for creating transaction")

        try:
            tx_json_data = copy.deepcopy(tx_json_data)
            tx_json_data["input"]["signature"] = signature_from_str(
                tx_json_data["input"]["signature"]
            )
            tx_json_data["input"]["public_key"] = public_key_from_str(
                tx_json_data["input"]["public_key"]
            )
            return Transaction(**tx_json_data)

        except KeyError as e:
            raise Exception(f"Invalid transaction JSON: missing field {e}") from e

        except Exception as e:
            raise Exception(f"Invalid transaction JSON: {e}") from e

    @staticmethod
    def is_valid(tx: Transaction) -> None:

        if tx.input["amount"] != sum(tx.output.values()):
            raise Exception(
                f"Invalid transaction {tx.id}: output amounts do not match the input amount."
            )

        if not Wallet.verify(tx.input["public_key"], tx.output, tx.input["signature"]):
            raise Exception(f"Invalid transaction {tx.id}: The signature is invalid.")
