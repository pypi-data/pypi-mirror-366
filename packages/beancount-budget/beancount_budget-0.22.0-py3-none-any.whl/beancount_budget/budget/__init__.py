from collections.abc import Sequence
from copy import copy, deepcopy
from csv import DictReader, DictWriter, unix_dialect
from decimal import Decimal
from functools import cached_property
from pathlib import Path
from typing import Self

import click
from beancount.core.display_context import DisplayContext
from beancount.core.inventory import Inventory

from beancount_budget.beancount import BeancountData, PerCategory
from beancount_budget.config import Config
from beancount_budget.month import Month, PerMonth
from beancount_budget.moves import Moves
from beancount_budget.quota import CategoryQuota, load_quotas
from beancount_budget.ui import format_table, fzf, list_problems

from .rows import BudgetRow, FilterRows
from .util import AVAIL, check_bounds, get_by_depth, set_difference, track_moves

ZERO = Decimal(0)


class Budget:
    "Represents a monthly budget."

    data: PerCategory[PerMonth[Decimal]]
    categories: list[str]
    currency: str
    months: list[Month]
    path: Path
    path_quotas: Path
    dcontext: DisplayContext
    _expenses: PerMonth[PerCategory[Decimal]]
    _income: PerMonth[Decimal]

    def __init__(
        self,
        bc_data: BeancountData,
        currency: str,
        path: Path,
        path_quotas: Path,
    ) -> None:
        self.path = path
        self.path_quotas = path_quotas
        self.currency = currency
        self.dcontext = bc_data.metadata["dcontext"]

        def get_currency(inv: Inventory) -> Decimal:
            "Filter an Inventory from Beancount data to Budget's currency."
            return self.quantize(inv.get_currency_units(currency).number or ZERO)

        self._expenses = {
            month: {category: get_currency(inv) for category, inv in expenses.items()}
            for month, expenses in bc_data.expenses.items()
        }
        self._income = {
            month: get_currency(inv) for month, inv in bc_data.net_income.items()
        }

        self.categories = bc_data.budget_categories
        self.months = bc_data.months

        if path.exists():
            self.load_csv(path)
        else:
            self.data = self.blank_budget

    @cached_property
    def zero(self):
        "Return a zero value formatted according to this budget's currency."
        return self.quantize(ZERO)

    @check_bounds
    def __getitem__(self, month: Month) -> PerCategory[Decimal]:
        "Return a copy of the data for the given month."
        return {category: row[month] for category, row in self.data.items()}

    def __deepcopy__(self, memo: dict) -> Self:
        "Deeply copy a Budget's `data`; the other attributes are shallowly copied."
        ret = copy(self)
        ret.data = deepcopy(self.data, memo)
        return ret

    @classmethod
    def from_config(cls, c: Config, currency: str | None = None) -> Self:
        "Load a Budget using paths from a Config."
        bcd = BeancountData(c.paths.beancount, c.regexes, c.remaps)
        currency = currency or c.default_currency
        return cls(
            bcd,
            currency,
            c.paths.budgets / f"{currency}.csv",
            c.paths.quotas / f"{currency}.toml",
        )

    @property
    def blank_budget(self) -> PerCategory[PerMonth[Decimal]]:
        "Return a budget with all zeroes (without modifying this one)."
        return {c: {m: self.zero for m in self.months} for c in self.categories}

    def reinit(self, verbose: bool = False) -> None:
        "Clear this budget's data then fill each month in order."
        self.data = self.blank_budget
        for month in self.months:
            for action in ("trim", "fill"):
                moves = getattr(self, action)(month)
                if verbose:
                    click.echo(f"{action.upper()} {month} {'=' * 40}\n{moves}")

    # Not bounds-checked, to avoid an infinite loop.
    def extend(self, month: Month) -> None:
        "Add a month (absent from Beancount data) to the budget."
        # It's assumed that the month being added is one after the last.
        assert month - 1 == self.months[-1]

        self.months.append(month)
        for cat in self.categories:
            self.data[cat][month] = self.zero
        self._income[month] = self.zero
        self._expenses[month] = {}

    def load_csv(self, path: Path) -> None:
        "Deserialize budget from CSV file(-like)."
        self.data = {}
        with open(path, encoding="utf-8") as f:
            reader = DictReader(f)
            for row in reader:
                category = row.pop("category")
                self.data[category] = {
                    Month.from_str(month): Decimal(amt) for month, amt in row.items()
                }

        # Handle categories missing from either budget's or Beancount's data.
        # (E.g., categories with no budgeted amounts are never written to disk.)
        keys_from_file = self.data.keys()
        if new_categories := set_difference(self.categories, keys_from_file):
            zeroes = {month: self.zero for month in self.months}
            self.data.update({cat: zeroes.copy() for cat in new_categories})
        if deleted_categories := set_difference(keys_from_file, self.categories):
            list_problems(
                "Budget has categories that Beancount data doesn't:",
                deleted_categories,
            )
            self.categories.extend(deleted_categories)
            # Categories came sorted from BCD, so maintain the status quo.
            self.categories.sort()

        # Handle months absent from BC data; user may have already filled
        # the budget for the new month. `B.extend` reads `self.categories`
        # so this step must come after categories are extended.
        assert reader.fieldnames  # placate mypy
        budget_months = [
            Month.from_str(s) for s in reader.fieldnames if s != "category"
        ]
        if new_months := set_difference(budget_months, self.months):
            for month in sorted(new_months):
                self.extend(month)

        # Handle months absent from budget (CSV) data; e.g., user may have
        # multiple currencies but infrequent transactions in one of them.
        if missing_months := set_difference(self.months, budget_months):
            for month in sorted(missing_months):
                for cat in self.categories:
                    self.data[cat][month] = self.zero

    def write(self) -> None:
        "Serialize budget to CSV file."
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            wrt = DictWriter(
                f,
                fieldnames=["category", *map(str, self.months)],
                dialect=unix_dialect,
            )
            wrt.writeheader()

            for cat in self.categories:
                # Write only categories with budgeted amounts, for space efficiency.
                if set(self.data[cat].values()) != {self.zero}:
                    months = {str(month): amt for month, amt in self.data[cat].items()}
                    wrt.writerow({"category": cat, **months})

    @check_bounds
    def set_amt(self, month: Month, category: str, amount: Decimal) -> None:
        "Set a budgeted amount."
        self.data[category][month] = amount

    @check_bounds
    def add(self, month: Month, category: str, amount: Decimal) -> None:
        "Add an amount to the budget."
        self.data[category][month] += amount

    @check_bounds
    def sub(self, month: Month, category: str, amount: Decimal) -> None:
        "Subtract an amount from the budget."
        # More readable than `b.add(..., -amount)`.
        self.data[category][month] -= amount

    @check_bounds
    def expenses(self, month: Month) -> PerCategory[Decimal]:
        "Return expenses for the given month."
        return self._expenses.get(month, {})

    @check_bounds
    def income(self, month: Month) -> Decimal:
        "Return net income for the given month."
        return self._income[month]

    # Months are traversed start-to-end via recursion, so an implicit
    # bounds-check won't suffice.
    @check_bounds
    def balances(self, month: Month) -> PerCategory[Decimal]:
        "Return budget balances for the given month."
        # This is not as expensive as it looks, despite being O(n^2).
        # `timeit` showed ~1 ms to add up ~1100 category-months on an R5 3600.
        # A hundred categories over a decade would take ~10 ms.

        def prev_balances(self, month: Month):
            if month == self.months[0]:
                return {c: self.zero for c in self.categories + [AVAIL]}
            return self.balances(month - 1)

        ret = prev_balances(self, month)

        budgeted = self[month]
        spent = self.expenses(month)
        for category in budgeted:
            ret[category] += budgeted.get(category, self.zero)
            ret[category] -= spent.get(category, self.zero)

        ret[AVAIL] += self.income(month) - sum(budgeted.values())

        return ret

    @cached_property
    def quotas(self) -> PerCategory[CategoryQuota]:
        "Load this budget's quotas."
        out = (
            load_quotas(self.path_quotas, self.quantize)
            if self.path_quotas.exists()
            else {}
        )
        if wrong_qnames := set_difference(out, self.categories):
            list_problems(
                "Found mismatched category names between quota(s) and budget:",
                wrong_qnames,
            )
        return out

    # Implicitly bounds-checked by `self.quotas`.
    def show_quotas(self, month: Month) -> str:
        "Show quota amounts for the given month."
        if not self.quotas:
            return ""

        headers = ("Name", "Type", "Req'd balance", "Req'd budget")
        table: list[tuple] = [headers]
        for category, cquota in self.quotas.items():
            table.extend(cquota.show(category, month))
            table.append((None, None, None, None))  # Blank line for readability
        table.pop()  # rm last blank line

        return format_table(
            table,
            headers=("N", "T", "RBa", "RBu"),
            numerical_headers=("RBa", "RBu"),
        )

    # Implicitly bounds-checked by `self.__getitem__`.
    def deviations(self, month: Month) -> PerCategory[Decimal]:
        "Return all quota deviations in the budget."
        ret = {}
        budget = self[month]

        for category, balance in self.balances(month).items():
            budgeted = budget.get(category, self.zero)
            cquota = self.quotas.get(category, CategoryQuota({}))
            ret[category] = cquota.deviation(month, budgeted, balance)

        return ret

    def quantize(self, amount: Decimal) -> Decimal:
        "Quantize a value with this budget's currency's display context."
        return self.dcontext.quantize(amount, self.currency)

    # Implicitly bounds-checked (along with all `track_moves` methods)
    # by `self.balances`.
    def moves(self, month: Month) -> Moves:
        "Generate a Moves object to be used in `track_moves` methods."
        return Moves(self.balances(month), self.deviations(month))

    @track_moves
    def cli_add(self, month: Month, category: str, amount: Decimal) -> Moves:
        "Execute `budget add` as a Move."
        moves = self.moves(month)
        moves.stage(AVAIL, category, self.quantize(amount))
        return moves

    @track_moves
    def cli_sub(self, month: Month, category: str, amount: Decimal) -> Moves:
        "Execute `budget sub` as a Move."
        moves = self.moves(month)
        moves.stage(category, AVAIL, self.quantize(amount))
        return moves

    @track_moves
    def trim(self, month: Month, dry_run: bool = False) -> Moves:
        "Remove surpluses from overbudgeted categories."
        moves = self.moves(month)

        for category, amount in moves.deviations.items():
            if amount > 0 and category != AVAIL:
                moves.stage(category, AVAIL, amount)

        return moves

    @track_moves
    def fill(self, month: Month, dry_run: bool = False) -> Moves:
        "Assign budget amounts until quotas are met and no negative balances remain."
        # My expense categories are named to sort by importance, so `B.fill`
        # has the elegant side-effect of draining the "available" envelope
        # first for rent, then for groceries, and so on.
        moves = self.moves(month)

        while shortfalls := {
            category: -deviation
            for category, deviation in moves.deviations.items()
            if deviation < 0
        }:
            for category, shortfall in shortfalls.items():
                if dry_run:
                    click.echo(
                        f"{category} (bal: {moves.balances[category]}, b: {self[month][category]}) "
                        f"is short {shortfall}"
                    )
                    continue

                # Fill from available
                if moves.balances[AVAIL] >= shortfall:
                    moves.stage(AVAIL, category, shortfall)

                # Partially fill from available
                elif moves.balances[AVAIL] > 0:
                    moves.stage(AVAIL, category, moves.balances[AVAIL])

                # Attempt fill from another category
                else:
                    click.echo(
                        "You've budgeted more money than you have."
                        if category == AVAIL
                        else f"{category} is overspent."
                    )

                    choices = [
                        f"{cat} ({amt})"
                        for cat, amt in moves.deviations.items()
                        if amt > 0 and cat != AVAIL
                    ]
                    if not choices:
                        click.echo("But there's no money left in the budget.")
                        return moves

                    click.echo(f"Take {shortfall} from which envelope?")
                    choice = fzf(choices).split(" ")[0]
                    to_move = min(shortfall, moves.balances[choice])

                    moves.stage(choice, category, to_move)
            if dry_run:
                # No budget data was or will be modified,
                # so bounce at the first pass.
                return moves

        return moves

    # Implicitly bounds-checked by `self.__getitem__`.
    def table(
        self,
        month: Month,
        depth: int | None = None,
        filter: FilterRows = FilterRows.DEFAULT,
        all_months: bool = False,
    ) -> list[tuple]:
        "Summarize a month in a two-dimensional list keyed by category."
        ret = []

        def dict_zip(
            *dicts: PerCategory[Decimal],
            filler=self.zero,
        ) -> PerCategory[BudgetRow]:
            # https://codereview.stackexchange.com/a/160584
            all_keys = {k for d in dicts for k in d.keys()}
            return {k: BudgetRow(*(d.get(k, filler) for d in dicts)) for k in all_keys}

        def get(data: PerCategory[Decimal]) -> PerCategory[Decimal]:
            return get_by_depth(data, depth) if depth else data

        def add_row(name: str, row: BudgetRow) -> None:
            ret.append((month, name, *row) if all_months else (name, *row))

        data = dict_zip(
            get(self[month]),
            get(self.expenses(month)),
            get(self.balances(month)),
            get(self.deviations(month)),
        )
        available = data.pop(AVAIL).balance
        totals = BudgetRow(
            *(
                sum(getattr(row, field) for row in data.values())
                for field in BudgetRow._fields
            )
        )

        for category, row in sorted(data.items()):  # sorted by category
            if filter.test(row):
                add_row(category, row)

        add_row("Total", totals)
        add_row(
            "Available", BudgetRow(None, None, available, available + totals.deviation)
        )
        add_row("Net income", BudgetRow(None, None, self.income(month), None))

        return ret

    # Implicitly bounds-checked by `self.table`.
    def format(
        self,
        month: Month,
        depth: int | None = None,
        filter: FilterRows = FilterRows.DEFAULT,
        all_months: bool = False,
        csv: bool = False,
    ) -> str:
        months = self.months if all_months else [month]

        numerical_headers = ["Budgeted", "Expenses", "Balances", "Deviations"]
        headers = ["Category"] + numerical_headers
        if all_months:
            headers.insert(0, "Month")
        table: list[Sequence] = [headers]

        for m in months:
            for row in self.table(m, depth, filter, all_months):
                table.append(row)

        return format_table(table, headers, numerical_headers, csv)
