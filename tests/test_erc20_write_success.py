from decimal import Decimal
from unittest.mock import patch

import pytest
from web3 import Web3

from dexsnake import ERC20Token

TOKEN = Web3.to_checksum_address("0x0000000000000000000000000000000000000001")
OTHER_TOKEN = Web3.to_checksum_address("0x0000000000000000000000000000000000000002")
DESTINATION = Web3.to_checksum_address("0x0000000000000000000000000000000000000003")
PRIVATE_KEY = "0x" + "01".zfill(64)
OWNER = Web3().eth.account.from_key(PRIVATE_KEY).address


def event_log(name, address=TOKEN, owner=OWNER, destination=DESTINATION, value=10):
    topics = [Web3.keccak(text=f"{name}(address,address,uint256)")]
    topics.extend(
        bytes.fromhex(account[2:]).rjust(32, b"\0") for account in (owner, destination)
    )
    return {
        "address": address,
        "topics": topics,
        "data": value.to_bytes(32, "big"),
        "blockNumber": 1,
        "transactionHash": b"\x01" * 32,
        "transactionIndex": 0,
        "blockHash": b"\x02" * 32,
        "logIndex": 0,
        "removed": False,
    }


@pytest.mark.parametrize(
    "method,event_name", [("approve", "Approval"), ("transfer", "Transfer")]
)
def test_write_requires_matching_token_event(method, event_name):
    token = ERC20Token(Web3(), TOKEN)
    token._decimals = 0
    receipt = {"status": 1, "logs": [], "transactionHash": b"\x01" * 32}

    with patch("dexsnake.erc20_token._send_transaction", return_value=receipt):
        with pytest.raises(RuntimeError, match="could not be confirmed") as error:
            getattr(token, method)(DESTINATION, Decimal(10), PRIVATE_KEY)
        assert Web3.to_hex(receipt["transactionHash"]) in str(error.value)

        receipt["logs"] = [event_log(event_name, address=OTHER_TOKEN)]
        with pytest.raises(RuntimeError, match="could not be confirmed"):
            getattr(token, method)(DESTINATION, Decimal(10), PRIVATE_KEY)

        receipt["logs"] = [event_log(event_name, value=9)]
        with pytest.raises(RuntimeError, match="could not be confirmed"):
            getattr(token, method)(DESTINATION, Decimal(10), PRIVATE_KEY)

        for mismatched_log in (
            event_log(event_name, owner=OTHER_TOKEN),
            event_log(event_name, destination=OTHER_TOKEN),
        ):
            receipt["logs"] = [mismatched_log]
            with pytest.raises(RuntimeError, match="could not be confirmed"):
                getattr(token, method)(DESTINATION, Decimal(10), PRIVATE_KEY)

        receipt["logs"] = [event_log(event_name)]
        assert getattr(token, method)(DESTINATION, Decimal(10), PRIVATE_KEY) is receipt
