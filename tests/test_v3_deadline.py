from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from dexsnake.uniswap_v3.router import UniswapV3Router


@pytest.mark.parametrize(
    "method_name,function_name,amounts",
    [
        (
            "exact_input_single",
            "exactInputSingle",
            {"amount_in": Decimal("1"), "amount_out_min": Decimal("1")},
        ),
        (
            "exact_output_single",
            "exactOutputSingle",
            {"amount_out": Decimal("1"), "amount_in_max": Decimal("1")},
        ),
    ],
)
@pytest.mark.parametrize("deadline", [1234, None])
def test_swap_deadline_is_enforced_by_multicall(
    method_name, function_name, amounts, deadline
):
    web3 = MagicMock()
    web3.to_checksum_address.side_effect = lambda address: address
    web3.eth.account.sign_transaction.return_value = SimpleNamespace(
        raw_transaction=b"signed transaction"
    )
    web3.eth.send_raw_transaction.return_value = b"transaction hash"
    router = object.__new__(UniswapV3Router)
    router.web3 = web3
    router.contract = MagicMock()
    router.contract.encode_abi.return_value = "0xswap"
    router.contract.functions.multicall.return_value.build_transaction.return_value = {}

    with patch(
        "dexsnake.uniswap_v3.router.ERC20Token",
        return_value=SimpleNamespace(decimals=18),
    ), patch("dexsnake.uniswap_v3.router.time.time", return_value=1000):
        getattr(router, method_name)(
            **amounts,
            token_in="0xin",
            token_out="0xout",
            fee=3000,
            recipient="0xto",
            account="0xaccount",
            private_key="key",
            deadline=deadline,
            gas=21000,
            gas_price=1,
        )

    router.contract.encode_abi.assert_called_once()
    assert router.contract.encode_abi.call_args.args[0] == function_name
    params = router.contract.encode_abi.call_args.kwargs["args"][0]
    assert "deadline" not in params
    router.contract.functions.multicall.assert_called_once_with(
        1300 if deadline is None else deadline, ["0xswap"]
    )
    web3.eth.send_raw_transaction.assert_called_once_with(b"signed transaction")
