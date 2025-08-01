from collections import namedtuple
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from beancount_budget.month import Month

from .quantize import FALLBACK_ZERO, Quantizer, two_places
from .types import Quota

QuotaRow = namedtuple(
    "QuotaRow",
    ("name", "type", "reqd_balance", "reqd_budget"),
    defaults=([None, None, None, None]),
)


@dataclass(frozen=True)
class CategoryQuota:
    "Represents the sum of quotas for a single category."

    quotas: dict[str, Quota]
    quantize: Quantizer = two_places

    def __post_init__(self):
        "Ensure `self.zero` is quantized correctly."
        object.__setattr__(self, "zero", self.quantize(FALLBACK_ZERO))

    @classmethod
    def from_dict(cls, data: dict, quantize: Quantizer = two_places) -> Self:
        "Deserialize a CategoryQuota from a dictionary."
        return cls(
            {qname: Quota.from_dict(qdata, quantize) for qname, qdata in data.items()},
            quantize,
        )

    def required_budget(self, month: Month) -> Decimal:
        "Return the amount to be budgeted to meet this quota."
        return (
            sum(q.required_budget(month) or q.zero for q in self.quotas.values())
            or FALLBACK_ZERO  # COMBAK: not `self.zero`?
        )

    def required_balance(self, month: Month) -> Decimal:
        "Return the amount to remain available to meet this quota."
        return (
            sum(q.required_balance(month) or q.zero for q in self.quotas.values())
            or FALLBACK_ZERO  # COMBAK: not `self.zero`?
        )

    def deviation(self, month: Month, budgeted: Decimal, balance: Decimal) -> Decimal:
        "Return the difference between budgeted and expected amounts."
        deviation = balance - self.required_balance(month)
        if reqd_budget := self.required_budget(month):  # COMBAK: `... is not None`?
            return min(budgeted - reqd_budget, deviation)
        return deviation

    def show(self, category: str, month: Month) -> list[QuotaRow]:
        "Visualize each quota's contribution to this category-quota."
        ret = [
            QuotaRow(
                category,
                None,
                self.required_balance(month),
                self.required_budget(month),
            )
        ]

        for name, quota in self.quotas.items():
            ret.append(
                QuotaRow(
                    f"- {name}",
                    str(quota),
                    reqd_balance=quota.required_balance(month),
                    reqd_budget=quota.required_budget(month),
                )
            )

        return ret
