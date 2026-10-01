import unittest
from decimal import Decimal, localcontext
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from dexsnake.uniswap_v2.router import UniswapV2Router
from dexsnake.uniswap_v3.router import UniswapV3Router


COMMON = {
    "account": "account",
    "private_key": "key",
    "deadline": 1234,
    "gas": 21000,
    "gas_price": 1,
}
AMOUNT_IN = Decimal("1.000000000000000001")
AMOUNT_OUT = Decimal("2.000001")
SCENARIOS = (
    (
        UniswapV2Router,
        "swap_exact_tokens_for_tokens",
        "swapExactTokensForTokens",
        {
            **COMMON,
            "amount_in": AMOUNT_IN,
            "amount_out_min": AMOUNT_OUT,
            "path": ["in", "out"],
            "to": "recipient",
        },
        (1_000_000_000_000_000_001, 2_000_001),
    ),
    (
        UniswapV2Router,
        "swap_tokens_for_exact_tokens",
        "swapTokensForExactTokens",
        {
            **COMMON,
            "amount_out": AMOUNT_OUT,
            "amount_in_max": AMOUNT_IN,
            "path": ["in", "out"],
            "to": "recipient",
        },
        (2_000_001, 1_000_000_000_000_000_001),
    ),
    (
        UniswapV3Router,
        "exact_input_single",
        "exactInputSingle",
        {
            **COMMON,
            "amount_in": AMOUNT_IN,
            "amount_out_min": AMOUNT_OUT,
            "token_in": "in",
            "token_out": "out",
            "fee": 3000,
            "recipient": "recipient",
        },
        (1_000_000_000_000_000_001, 2_000_001),
    ),
    (
        UniswapV3Router,
        "exact_output_single",
        "exactOutputSingle",
        {
            **COMMON,
            "amount_out": AMOUNT_OUT,
            "amount_in_max": AMOUNT_IN,
            "token_in": "in",
            "token_out": "out",
            "fee": 3000,
            "recipient": "recipient",
        },
        (2_000_001, 1_000_000_000_000_000_001),
    ),
)


class RouterAmountTests(unittest.TestCase):
    def make_router(self, cls):
        router = object.__new__(cls)
        router.web3 = MagicMock()
        router.web3.to_checksum_address.side_effect = lambda address: address
        router.web3.eth.account.sign_transaction.return_value = SimpleNamespace(
            raw_transaction=b"signed"
        )
        router.contract = MagicMock()
        router.contract.encode_abi.return_value = "0xswap"
        return router

    def call_swap(self, router, method_name, kwargs):
        decimals = {"in": 18, "out": 6}
        with patch(
            f"{type(router).__module__}.ERC20Token",
            side_effect=lambda web3, address: SimpleNamespace(
                decimals=decimals[address]
            ),
        ):
            return getattr(router, method_name)(**kwargs)

    def test_all_swaps_use_exact_base_units(self):
        for cls, method_name, contract_function, kwargs, expected in SCENARIOS:
            with self.subTest(method=method_name):
                router = self.make_router(cls)
                with localcontext() as context:
                    context.prec = 6
                    self.call_swap(router, method_name, kwargs)

                if cls is UniswapV2Router:
                    call = getattr(
                        router.contract.functions, contract_function
                    ).call_args
                    self.assertEqual(call.args[:2], expected)
                else:
                    call = router.contract.encode_abi.call_args
                    self.assertEqual(call.args[0], contract_function)
                    params = call.kwargs["args"][0]
                    fields = (
                        ("amountIn", "amountOutMinimum")
                        if method_name == "exact_input_single"
                        else ("amountOut", "amountInMaximum")
                    )
                    self.assertEqual(tuple(params[field] for field in fields), expected)

    def test_unrepresentable_amounts_fail_before_swap_build(self):
        for cls, method_name, contract_function, kwargs, _ in SCENARIOS:
            for amount_name in (
                ("amount_in", "amount_out_min")
                if "amount_in" in kwargs
                else ("amount_out", "amount_in_max")
            ):
                with self.subTest(method=method_name, amount=amount_name):
                    router = self.make_router(cls)
                    bad_kwargs = kwargs.copy()
                    bad_kwargs[amount_name] = (
                        Decimal("0.0000001")
                        if amount_name in ("amount_out", "amount_out_min")
                        else Decimal("0.0000000000000000001")
                    )
                    with self.assertRaisesRegex(ValueError, "decimal places"):
                        self.call_swap(router, method_name, bad_kwargs)

                    if cls is UniswapV2Router:
                        getattr(
                            router.contract.functions, contract_function
                        ).assert_not_called()
                    else:
                        router.contract.encode_abi.assert_not_called()
                    router.web3.eth.account.sign_transaction.assert_not_called()


if __name__ == "__main__":
    unittest.main()
