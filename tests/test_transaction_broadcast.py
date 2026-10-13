from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from dexsnake import ERC20Token
from dexsnake.transactions import _send_transaction
from dexsnake.uniswap_v2.router import UniswapV2Router
from dexsnake.uniswap_v3.router import UniswapV3Router

COMMON = {"private_key": "key", "gas": 21000, "gas_price": 1}


@pytest.mark.parametrize(
    "cls,method_name,contract_function,kwargs",
    [
        (
            ERC20Token,
            "approve",
            "approve",
            {**COMMON, "spender": "0xspender", "value": Decimal("1")},
        ),
        (
            ERC20Token,
            "transfer",
            "transfer",
            {**COMMON, "to": "0xto", "value": Decimal("1")},
        ),
        (
            UniswapV2Router,
            "swap_exact_tokens_for_tokens",
            "swapExactTokensForTokens",
            {
                **COMMON,
                "amount_in": Decimal("1"),
                "amount_out_min": Decimal("1"),
                "path": ["0xin", "0xout"],
                "to": "0xto",
                "deadline": 1,
            },
        ),
        (
            UniswapV2Router,
            "swap_tokens_for_exact_tokens",
            "swapTokensForExactTokens",
            {
                **COMMON,
                "amount_out": Decimal("1"),
                "amount_in_max": Decimal("1"),
                "path": ["0xin", "0xout"],
                "to": "0xto",
                "deadline": 1,
            },
        ),
        (
            UniswapV3Router,
            "exact_input_single",
            "exactInputSingle",
            {
                **COMMON,
                "amount_in": Decimal("1"),
                "amount_out_min": Decimal("1"),
                "token_in": "0xin",
                "token_out": "0xout",
                "fee": 3000,
                "recipient": "0xto",
                "deadline": 1,
            },
        ),
        (
            UniswapV3Router,
            "exact_output_single",
            "exactOutputSingle",
            {
                **COMMON,
                "amount_out": Decimal("1"),
                "amount_in_max": Decimal("1"),
                "token_in": "0xin",
                "token_out": "0xout",
                "fee": 3000,
                "recipient": "0xto",
                "deadline": 1,
            },
        ),
    ],
)
@pytest.mark.parametrize("status", [0, 1])
def test_write_methods_handle_receipts(
    cls, method_name, contract_function, kwargs, status
):
    web3 = MagicMock()
    web3.to_checksum_address.side_effect = lambda address: address
    web3.eth.account.from_key.return_value.address = "0xaccount"
    web3.eth.get_transaction_count.return_value = 0
    web3.eth.account.from_key.return_value.sign_transaction.return_value = (
        SimpleNamespace(raw_transaction=b"signed transaction")
    )
    web3.eth.send_raw_transaction.return_value = b"transaction hash"
    receipt = {"status": status}
    web3.eth.wait_for_transaction_receipt.return_value = receipt

    instance = object.__new__(cls)
    instance.web3 = web3
    instance.contract = MagicMock()
    instance.address = "0xtoken"
    instance._decimals = 18
    if cls is ERC20Token:
        event_name = "Approval" if method_name == "approve" else "Transfer"
        event_args = (
            {"owner": "0xaccount", "spender": "0xspender", "value": 10**18}
            if method_name == "approve"
            else {"from": "0xaccount", "to": "0xto", "value": 10**18}
        )
        getattr(instance.contract.events, event_name)().process_receipt.return_value = [
            {"address": "0xtoken", "args": event_args}
        ]
    function = getattr(instance.contract.functions, contract_function)
    build_transaction = (
        instance.contract.functions.multicall.return_value.build_transaction
        if cls is UniswapV3Router
        else function.return_value.build_transaction
    )
    build_transaction.return_value = {}

    with patch(
        f"{cls.__module__}.ERC20Token", return_value=SimpleNamespace(decimals=18)
    ):
        if status == 0:
            with pytest.raises(RuntimeError) as error:
                getattr(instance, method_name)(**kwargs)
            assert "0x" + b"transaction hash".hex() in str(error.value)
        else:
            assert getattr(instance, method_name)(**kwargs) is receipt

    if cls is UniswapV3Router:
        instance.contract.encode_abi.assert_called_once()
    build_transaction.assert_called_once_with(
        {"from": "0xaccount", "nonce": 0, "gasPrice": 1, "gas": 21000}
    )
    web3.eth.get_transaction_count.assert_called_once_with("0xaccount", "pending")
    assert web3.eth.account.from_key.call_count == (
        2 if cls is ERC20Token and status == 1 else 1
    )
    web3.eth.account.from_key.assert_called_with("key")
    web3.eth.estimate_gas.assert_not_called()
    web3.eth.account.from_key.return_value.sign_transaction.assert_called_once()
    web3.eth.send_raw_transaction.assert_called_once_with(b"signed transaction")
    web3.eth.wait_for_transaction_receipt.assert_called_once_with(b"transaction hash")


def test_unspecified_gas_is_left_for_web3_to_estimate():
    web3 = MagicMock()
    web3.to_checksum_address.side_effect = lambda address: address
    web3.eth.account.from_key.return_value.address = "0xaccount"
    web3.eth.gas_price = 1
    web3.eth.get_transaction_count.return_value = 0
    web3.eth.account.from_key.return_value.sign_transaction.return_value = (
        SimpleNamespace(raw_transaction=b"signed transaction")
    )
    web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
    function = MagicMock()
    function.build_transaction.return_value = {}

    _send_transaction(web3, function, "key", None, None)

    function.build_transaction.assert_called_once_with(
        {"from": "0xaccount", "nonce": 0, "gasPrice": 1}
    )
    web3.eth.account.from_key.assert_called_once_with("key")
    web3.eth.estimate_gas.assert_not_called()
