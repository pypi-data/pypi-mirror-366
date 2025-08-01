"""Quotas can be input as arbitrarily precise floating points (e.g., a £100.00
quota written as `100`), but must conform to the format Beancount determines
for the currency. Neither format nor currency is known ahead of time, so the
`Budget` loading the `Quotas` must provide a quantizer.
"""

from collections.abc import Callable
from decimal import Decimal

type Quantizer = Callable[[Decimal], Decimal]
FALLBACK_ZERO = Decimal("0.00")


def two_places(x: Decimal) -> Decimal:
    """Quantize an amount to two decimal places.

    As of 2025: of the ten most-traded currencies by value, nine have sub-units
    of a hundredth. The remaining one is the yen, which has no sub-units.
    """
    return x.quantize(FALLBACK_ZERO)
