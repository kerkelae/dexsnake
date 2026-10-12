from decimal import Decimal, localcontext
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from dexsnake import ERC20Token
from dexsnake.amounts import _to_base_units


def make_token(decimals=6):
    token = ERC20Token.__new__(ERC20Token)
    token._decimals = decimals
    token.contract = Mock()
    token.web3 = Mock()
    token.web3.to_checksum_address.side_effect = lambda address: address
    token.web3.eth.account.from_key.return_value.address = "account"
    token.web3.eth.gas_price = 1
    token.web3.eth.get_transaction_count.return_value = 0
    token.web3.eth.estimate_gas.return_value = 100_000
    token.web3.eth.account.from_key.return_value.sign_transaction.return_value = (
        SimpleNamespace(raw_transaction=b"signed")
    )
    token.web3.eth.send_raw_transaction.return_value = b"hash"
    token.web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
    token.contract.functions.approve.return_value.build_transaction.return_value = {}
    token.contract.functions.transfer.return_value.build_transaction.return_value = {}
    return token


@pytest.mark.parametrize("method", ("approve", "transfer"))
def test_approve_and_transfer_use_exact_base_units(method):
    token = make_token()
    with localcontext() as context:
        context.prec = 4
        receipt = getattr(token, method)(
            "destination", Decimal("123456789.123456"), "key"
        )

    assert receipt == {"status": 1}
    getattr(token.contract.functions, method).assert_called_once_with(
        "destination", 123456789123456
    )


def test_zero_and_integer_amounts_are_exact():
    assert _to_base_units(Decimal("0"), 6) == 0
    assert _to_base_units(2, 6) == 2_000_000
    assert _to_base_units(Decimal("1.000000"), 6) == 1_000_000


@pytest.mark.parametrize("method", ("approve", "transfer"))
def test_overprecision_is_rejected_before_building_transaction(method):
    token = make_token()
    with pytest.raises(ValueError, match="decimal places"):
        getattr(token, method)("destination", Decimal("1.0000001"), "key")
    getattr(token.contract.functions, method).assert_not_called()
    token.web3.eth.send_raw_transaction.assert_not_called()


@pytest.mark.parametrize("value", (0.1, True, "1"))
def test_invalid_types_are_rejected(value):
    with pytest.raises(TypeError):
        _to_base_units(value, 6)


@pytest.mark.parametrize("value", (Decimal("-1"), Decimal("NaN"), Decimal("Infinity")))
def test_invalid_values_are_rejected(value):
    with pytest.raises(ValueError):
        _to_base_units(value, 6)


def test_uint256_overflow_is_rejected():
    with pytest.raises(ValueError, match="uint256"):
        _to_base_units(2**256, 0)
