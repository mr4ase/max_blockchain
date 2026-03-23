# backend\tests\wallet\conftest.py


from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.config import STARTING_BALANCE
import pytest


@pytest.fixture(scope="function")
def sender_wallet() -> Wallet:
    return Wallet()


@pytest.fixture(scope="function")
def recipient_wallet() -> Wallet:
    return Wallet()


@pytest.fixture(scope="session")
def test_amount_100() -> int:
    return 100
