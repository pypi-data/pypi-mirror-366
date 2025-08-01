from dataclasses import dataclass
from decimal import Decimal

from beancount_budget.month import Month

from .quantize import FALLBACK_ZERO, Quantizer, two_places


@dataclass(frozen=True)
class Quota:
    "Represents a single quota."

    amount: Decimal
    start: Month | None = None
    quantize: Quantizer = two_places
    zero: Decimal = FALLBACK_ZERO

    def __post_init__(self):
        "Ensure `self.amount` is quantized correctly."

        object.__setattr__(self, "amount", self.quantize(self.amount))
        object.__setattr__(self, "zero", self.quantize(FALLBACK_ZERO))

    @classmethod
    def from_dict(
        _, data: dict, quantize: Quantizer = two_places
    ):  # -> subclass of Quota (Monthly | Fixed | ...)
        "Deserialize a Quota from a dictionary."

        amount = Decimal(data["amount"])
        if start := data.get("start"):
            start = Month.from_str(start)

        common_args = {"amount": amount, "start": start, "quantize": quantize}

        if data.get("goal"):
            hold = data["goal"].get("hold", False)

            if isinstance(hold, str):
                hold = Month.from_str(hold)
            elif not isinstance(hold, bool):
                raise RuntimeError(
                    f"Expected month or bool for quota hold, got: {hold}"
                )

            if not start:
                raise RuntimeError("No start date for goal quota")

            return Goal(
                by=Month.from_str(data["goal"]["by"]),
                hold=hold,
                **common_args,
            )

        if data.get("yearly"):
            return Yearly(month=data["yearly"]["month"], **common_args)
        elif data.get("monthly", {}).get("fixed"):
            return Fixed(**common_args)
        else:
            return Monthly(**common_args)

    def required_balance(self, month: Month) -> Decimal | None:
        "Return the balance required to meet this quota."
        raise NotImplementedError

    def required_budget(self, month: Month) -> Decimal | None:
        return None


@dataclass(frozen=True, kw_only=True)
class Monthly(Quota):
    "Intended for regular expenses such as groceries or utilities."

    def __str__(self) -> str:
        return "monthly"

    def required_balance(self, month: Month) -> Decimal | None:
        if self.start and month < self.start:
            return None
        return self.amount


@dataclass(frozen=True, kw_only=True)
class Fixed(Quota):
    "Intended for regular, unvarying expenses such as mortgage payments."

    def __str__(self) -> str:
        return "monthly (fixed)"

    def required_balance(self, month: Month) -> Decimal | None:
        return None

    def required_budget(self, month: Month) -> Decimal | None:
        if self.start and month < self.start:
            return None
        return self.amount


@dataclass(frozen=True, kw_only=True)
class Goal(Quota):
    """Intended for planned one-time expenses such as vacations or repairs.

    The `target` argument represents the month _before_ which the quota should be met.
    For example:

        example_quota = Quota(
            amount=Decimal(4000),
            start=Month(2023, 1),
            by=Month(2023, 5),
        )

    This quota targets a ¤4000 purchase in May 2023, starting in January of
    that year. The saving occurs from January to April, inclusive, at a
    calculated rate of ¤1000 per month. In March there should be three months'
    worth of savings:

        example_quota.required_balance(Month(2023, 3)) == Decimal('3000.00')
    """

    start: Month
    by: Month
    hold: Month | bool = False

    def __str__(self) -> str:
        if isinstance(self.hold, Month):
            hold_status = f"; held until {self.hold}"
        elif self.hold:
            hold_status = "; held indefinitely"
        else:
            hold_status = ""

        return f"goal ({self.start} to {self.by}{hold_status})"

    def is_held(self, month: Month) -> bool:
        if isinstance(self.hold, bool):
            return self.hold
        elif isinstance(self.hold, Month):
            return month < self.hold

    def required_balance(self, month: Month) -> Decimal | None:
        if month < self.start:
            return None

        if month >= self.by:
            return self.amount if self.is_held(month) else self.zero

        all_months = self.start.delta(self.by)
        remaining_months = month.delta(self.by) - 1
        chunk = Decimal(self.amount / all_months)
        return self.quantize(chunk * (all_months - remaining_months))


@dataclass(frozen=True, kw_only=True)
class Yearly(Quota):
    "Intended for regular, unvarying expenses such as subscriptions."

    month: int

    def __str__(self) -> str:
        return f"yearly ({self.month})"

    def required_balance(self, month: Month) -> Decimal | None:
        if self.start and month < self.start:
            return None

        # `month` (method arg) is the month being calculated for.
        # `self.month` is the month on which the yearly quota recurs.
        by = month.next(self.month)
        return Goal(
            amount=self.amount, start=by - 12, by=by, quantize=self.quantize
        ).required_balance(month)
