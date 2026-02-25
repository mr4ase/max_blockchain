from backend.util.hex_to_binary import hex_to_binary, HEX_TO_BINARY_CONVERSION_TABLE
from backend.util.crypto_hash import crypto_hash


def test_hex_to_binary():
    test_num = 521
    hex_test_num = hex(test_num)[2:]
    binary_test_num = hex_to_binary(hex_test_num)

    assert test_num == int(binary_test_num, 2)
