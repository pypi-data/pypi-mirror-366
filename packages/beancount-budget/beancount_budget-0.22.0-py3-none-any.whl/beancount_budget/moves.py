from collections import defaultdict, namedtuple
from dataclasses import dataclass, field
from decimal import Decimal

from .beancount import PerCategory
from .ui import format_table

MovesRow = namedtuple("MovesRow", ("To", "From", "Amt"))

type MovesData = PerCategory[PerCategory[Decimal]]


def data_factory() -> MovesData:
    return defaultdict(lambda: defaultdict(Decimal))


@dataclass
class Moves:
    """Transfers to be made among budget categories.

    This type exists so that moves can be collected and summarized, instead of
    being printed one-by-one, which can quickly become unreadable.

    Changed balances are tracked independently of `Budget`s, so `Moves`es are
    instantiated with partial budget data.
    """

    # This class takes only what it needs from `Budget`,
    # to avoid circular imports.
    balances: PerCategory[Decimal]
    deviations: PerCategory[Decimal]
    data: MovesData = field(default_factory=data_factory)

    def __repr__(self) -> str:
        return f"Moves({self.data})"  # pragma: no cover

    def __str__(self) -> str:
        return format_table(
            self.table(for_tty=True),
            headers=MovesRow._fields,
            numerical_headers=("Amt",),
        )

    def stage(self, from_acct: str, to_acct: str, amt: Decimal) -> None:
        "Add a move to be tracked."
        if not amt:
            return

        self.data[to_acct][from_acct] += amt
        self.balances[from_acct] -= amt
        self.balances[to_acct] += amt
        if self.deviations:
            self.deviations[from_acct] -= amt
            self.deviations[to_acct] += amt

    def table(self, for_tty: bool = False) -> list[MovesRow]:
        "Output moves as a table."
        table = []

        def add_row(to_acct, from_acct, amount) -> None:
            table.append(MovesRow(to_acct, from_acct, amount))

        for to_acct, moves in self.data.items():
            add_row(to_acct, "(Balance now)", self.balances[to_acct])
            add_row(None, "(Balance added)", sum(moves.values()))
            for from_acct, amt in moves.items():
                add_row(None, from_acct, amt)
            if for_tty:
                table.append(MovesRow(None, None, None))  # Blank line for readability.

        if for_tty and table != []:
            # Rows are grouped by category, and their variable sizes
            # preclude anything cleaner like `more_itertools.intersperse`.
            # So pop the last blank line manually.
            table.pop()

        return table
