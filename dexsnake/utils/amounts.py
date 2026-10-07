from decimal import Decimal
from typing import Union


def _to_base_units(value: Union[Decimal, int], decimals: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int)):
        raise TypeError("Token amount must be a Decimal or integer")
    value = Decimal(value)
    if not value.is_finite() or value < 0:
        raise ValueError("Token amount must be finite and non-negative")

    numerator, denominator = value.as_integer_ratio()
    units, remainder = divmod(numerator * 10**decimals, denominator)
    if remainder:
        raise ValueError(f"Token amount exceeds {decimals} decimal places")
    if units >= 2**256:
        raise ValueError("Token amount exceeds uint256 range")
    return units
