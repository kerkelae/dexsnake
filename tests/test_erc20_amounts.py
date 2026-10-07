import unittest
from decimal import Decimal, localcontext
from types import SimpleNamespace
from unittest.mock import Mock

from dexsnake.utils.amounts import _to_base_units
from dexsnake.utils.erc20_token import ERC20Token


class ERC20AmountTests(unittest.TestCase):
    def make_token(self, decimals=6):
        token = ERC20Token.__new__(ERC20Token)
        token._decimals = decimals
        token.contract = Mock()
        token.web3 = Mock()
        token.web3.to_checksum_address.side_effect = lambda address: address
        token.web3.eth.gas_price = 1
        token.web3.eth.get_transaction_count.return_value = 0
        token.web3.eth.estimate_gas.return_value = 100_000
        token.web3.eth.account.sign_transaction.return_value = SimpleNamespace(
            raw_transaction=b"signed"
        )
        token.web3.eth.send_raw_transaction.return_value = b"hash"
        token.web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        token.contract.functions.approve.return_value.build_transaction.return_value = {}
        token.contract.functions.transfer.return_value.build_transaction.return_value = {}
        return token

    def test_approve_and_transfer_use_exact_base_units(self):
        for method in ("approve", "transfer"):
            with self.subTest(method=method):
                token = self.make_token()
                with localcontext() as context:
                    context.prec = 4
                    receipt = getattr(token, method)(
                        "destination", Decimal("123456789.123456"), "account", "key"
                    )

                self.assertEqual(receipt, {"status": 1})
                getattr(token.contract.functions, method).assert_called_once_with(
                    "destination", 123456789123456
                )

    def test_zero_and_integer_amounts_are_exact(self):
        self.assertEqual(_to_base_units(Decimal("0"), 6), 0)
        self.assertEqual(_to_base_units(2, 6), 2_000_000)
        self.assertEqual(_to_base_units(Decimal("1.000000"), 6), 1_000_000)

    def test_overprecision_is_rejected_before_building_transaction(self):
        for method in ("approve", "transfer"):
            with self.subTest(method=method):
                token = self.make_token()
                with self.assertRaisesRegex(ValueError, "decimal places"):
                    getattr(token, method)(
                        "destination", Decimal("1.0000001"), "account", "key"
                    )
                getattr(token.contract.functions, method).assert_not_called()
                token.web3.eth.send_raw_transaction.assert_not_called()

    def test_invalid_amounts_are_rejected(self):
        for value in (0.1, True, "1"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    _to_base_units(value, 6)
        for value in (Decimal("-1"), Decimal("NaN"), Decimal("Infinity")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _to_base_units(value, 6)
        with self.assertRaisesRegex(ValueError, "uint256"):
            _to_base_units(2**256, 0)


if __name__ == "__main__":
    unittest.main()
