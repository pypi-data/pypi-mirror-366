from dataclasses import dataclass
from datetime import date
from typing import Self

from dateutil.relativedelta import relativedelta


@dataclass(order=True, frozen=True)
class Month:
    "Rudimentary representation of a month in the budget."

    year: int
    month: int

    @classmethod
    def from_str(cls, string: str) -> Self:
        """Convert a string, e.g. "2023-12", to a Month."""
        year, month = map(int, string.split("-"))
        return cls(year, month)

    @classmethod
    def from_date(cls, d: date) -> Self:
        "Convert a datetime object to a Month."
        return cls(d.year, d.month)

    @classmethod
    def this(cls) -> Self:
        "Return current month."
        today = date.today()
        return cls(today.year, today.month)

    def __str__(self) -> str:
        return f"{self.year}-{self.month:02}"

    def __add__(self, i: int) -> Self:
        ret = date(self.year, self.month, 1) + relativedelta(months=i)
        return self.__class__(ret.year, ret.month)

    def __sub__(self, i: int) -> Self:
        return self.__add__(-i)

    def delta(self, other: Self) -> int:
        "Calculate number of months between self and other."
        return (other.year - self.year) * 12 + other.month - self.month

    def next(self, i: int) -> Self:
        "Return next occurrence of the given month."
        year = self.year if self.month < i else self.year + 1
        return self.__class__(year, i)


type PerMonth[T] = dict[Month, T]
