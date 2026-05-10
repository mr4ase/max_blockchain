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
from backend.config import MINING_REWARD, MINING_REWARD_INPUT


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

        input_data = {}

        for key, value in self.input.items():
            if key == "public_key":
                input_data[key] = public_key_to_str(self.input[key])
            elif key == "signature":
                input_data[key] = signature_to_str(self.input[key])
            else:
                input_data[key] = value

        return {
            "id": self.id,
            "input": input_data,
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

        if tx.input == MINING_REWARD_INPUT:
            if len(tx.output) != 1:
                raise Exception(f"Invalid number of miners in mining reward tx! Tx.id: {tx.id}")
            if list(tx.output.values()) != [MINING_REWARD]:
                raise Exception(f"Invalid mining reward amount in tx! Tx.id: {tx.id}")
            return

        if tx.input["amount"] != sum(tx.output.values()):
            raise Exception(
                f"Invalid transaction {tx.id}: output amounts do not match the input amount."
            )

        if not Wallet.verify(tx.input["public_key"], tx.output, tx.input["signature"]):
            raise Exception(f"Invalid transaction {tx.id}: The signature is invalid.")

    @staticmethod
    def reward_transaction(miner_wallet: Wallet) -> Transaction:
        output = {miner_wallet.address: MINING_REWARD}
        return Transaction(input=MINING_REWARD_INPUT, output=output)
