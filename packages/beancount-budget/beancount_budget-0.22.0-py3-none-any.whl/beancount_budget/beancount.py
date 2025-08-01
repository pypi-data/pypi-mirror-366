from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from re import Pattern
from typing import Any

from beancount.core.data import Entries, Open, Posting, Transaction, filter_txns
from beancount.core.inventory import Inventory
from beancount.core.realization import compute_postings_balance, postings_by_account
from beancount.loader import load_file

from .config import Regexes, Remaps
from .month import Month, PerMonth
from .ui import list_problems

type PerCategory[T] = dict[str, T]


def match(directive: Posting | Open | Transaction, regexes: Iterable[Pattern]) -> bool:
    "Return true if any of the regexes match the directive's account(s)."
    if isinstance(directive, Transaction):
        return any(r.search(p.account) for r in regexes for p in directive.postings)
    return any(r.search(directive.account) for r in regexes)


@dataclass
class BeancountData:
    "Data read from Beancount."

    path: Path
    regexes: Regexes
    remaps: Remaps = Remaps()
    entries: Entries = field(default_factory=list)
    errors: list = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.entries, self.errors, self.metadata = load_file(str(self.path))
        if self.errors:
            list_problems(
                "Errors found in Beancount data:",
                (f"{e.message}" for e in self.errors),
            )

    @cached_property
    def months(self) -> list[Month]:
        "Return the months this Beancount data spans."
        return list(self.by_month.keys())

    @cached_property
    def by_month(self) -> PerMonth[list[Transaction]]:
        "Return all transactions, grouped by month."
        out = defaultdict(list)
        for txn in filter_txns(self.entries):
            out[Month.from_date(txn.date)].append(txn)
        return dict(out)

    def is_flow(self, p: Posting) -> bool:
        "Return whether this Posting counts as a cash flow."
        return match(
            p,
            (
                self.regexes.cash,
                self.regexes.transfers,
                self.regexes.credit,
            ),
        )

    def cashflow(self, txns: Iterable[Transaction]) -> Inventory:
        "Return the total cashflow from a list of Transactions."
        return compute_postings_balance(
            p for txn in txns for p in txn.postings if self.is_flow(p)
        )

    # COMBAK: This won't hold up to a substantial category refactor;
    # budget data would have to be redone from scratch.
    @cached_property
    def budget_categories(self) -> list[str]:
        "Return all budgetable categories, sorted alphabetically."
        result = set(
            self.remaps.get(e.account)
            for e in self.entries
            if isinstance(e, Open)
            and match(
                e, (self.regexes.expenses, self.regexes.invest, self.regexes.loans)
            )
            and not self.regexes.deductions.search(e.account)
        )
        return sorted(result)

    @cached_property
    def net_income(self) -> PerMonth[Inventory]:
        """Return net income in each available month.

        Opening balances are included because existing budgeted funds
        (e.g., a large sum saved over time for a house's down payment)
        must come from somewhere.
        """

        def is_income(txn: Transaction) -> bool:
            return match(txn, (self.regexes.income, self.regexes.open))

        return {
            month: self.cashflow(t for t in txns if is_income(t))
            for month, txns in self.by_month.items()
        }

    @cached_property
    def expenses(self) -> PerMonth[PerCategory[Inventory]]:
        """Return expenses in each available month.

        "Expenses" is a word which here means "negative cashflows", so it includes
        transfers to non-cash accounts, e.g., brokerage accounts.
        """
        out: dict = defaultdict(lambda: defaultdict(Inventory))

        for month, txns in self.by_month.items():
            expense_txns = (
                t
                for t in txns
                if any(self.is_flow(p) for p in t.postings)
                and not match(t, (self.regexes.income,))
            )

            for account, postings in postings_by_account(expense_txns).items():
                account = self.remaps.get(account)
                if account in self.budget_categories:
                    out[month][account] += compute_postings_balance(postings)

        return dict(out)
