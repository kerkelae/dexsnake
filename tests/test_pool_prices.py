from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from dexsnake.uniswap_v2.pair import UniswapV2Pair
from dexsnake.uniswap_v3.pool import UniswapV3Pool


def test_v2_pair_price_uses_scaled_reserves():
    pair = object.__new__(UniswapV2Pair)
    pair.contract = MagicMock()
    pair.contract.functions.getReserves.return_value.call.return_value = (
        2 * 10**18,
        6_000 * 10**6,
        0,
    )
    pair._token_0 = SimpleNamespace(decimals=18)
    pair._token_1 = SimpleNamespace(decimals=6)

    assert pair.get_reserves() == (Decimal("2"), Decimal("6000"))
    assert pair.get_price() == Decimal("3000")


@pytest.mark.parametrize(
    "reserves",
    [
        (Decimal(0), Decimal(0)),
        (Decimal(0), Decimal(1)),
        (Decimal(1), Decimal(0)),
    ],
)
def test_v2_pair_without_both_reserves_has_no_price(reserves):
    pair = object.__new__(UniswapV2Pair)
    pair.get_reserves = MagicMock(return_value=reserves)

    with pytest.raises(ValueError, match="Pair has no price without both reserves"):
        pair.get_price()


def test_uninitialized_v3_pool_has_no_price():
    pool = object.__new__(UniswapV3Pool)
    pool.contract = MagicMock()
    pool.contract.functions.slot0.return_value.call.return_value = (0,)

    with pytest.raises(ValueError, match="Pool is not initialized"):
        pool.get_price()


@pytest.mark.parametrize(
    "decimals_0, decimals_1, expected",
    [
        (18, 6, Decimal("4000000000000")),
        (6, 18, Decimal("0.000000000004")),
    ],
)
def test_v3_pool_price_uses_token_decimals(decimals_0, decimals_1, expected):
    pool = object.__new__(UniswapV3Pool)
    pool.contract = MagicMock()
    pool.contract.functions.slot0.return_value.call.return_value = (2**97,)
    pool._token_0 = SimpleNamespace(decimals=decimals_0)
    pool._token_1 = SimpleNamespace(decimals=decimals_1)

    assert pool.get_price() == expected
