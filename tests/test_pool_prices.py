from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from dexsnake.uniswap_v2.pair import UniswapV2Pair
from dexsnake.uniswap_v3.pool import UniswapV3Pool


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
