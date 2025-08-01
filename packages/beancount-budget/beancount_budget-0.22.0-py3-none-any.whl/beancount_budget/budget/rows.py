from collections import namedtuple
from enum import StrEnum, auto

BudgetRow = namedtuple(
    "BudgetRow",
    ("budgeted", "expenses", "balance", "deviation"),
    defaults=([None, None, None, None]),
)


class FilterRows(StrEnum):
    """Specifies which rows of a Budget to show.

    Rows will be shown if they...
    - Default:   ...contain at least one non-zero value.
    - All:       ...exist.
    - Overspent: ...have a negative deviation.
    - Surplus:   ...have a positive deviation.
    """

    DEFAULT = auto()
    ALL = auto()
    OVERSPENT = auto()
    SURPLUS = auto()

    def test(self, row: BudgetRow) -> bool:
        "Return whether this row should be printed."
        match self.value:
            case "default":
                return any(row)
            case "all":
                return True
            case "overspent":
                return row.deviation < 0
            case "surplus":
                return row.deviation > 0
        raise NotImplementedError
