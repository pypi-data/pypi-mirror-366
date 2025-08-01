import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from re import Pattern, compile
from typing import Self


@dataclass(frozen=True)
class Regexes:
    "Patterns that categorize Beancount accounts."

    cash: Pattern
    credit: Pattern
    deductions: Pattern
    expenses: Pattern
    income: Pattern
    invest: Pattern
    loans: Pattern
    open: Pattern
    transfers: Pattern

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        return cls(**{k: compile(v) for k, v in data.items()})


@dataclass(frozen=True)
class Paths:
    "Paths to Beancount and budget data. Can be absolute or relative."

    beancount: Path
    budgets: Path
    quotas: Path

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        return cls(**{k: Path(v) for k, v in data.items()})


@dataclass(frozen=True)
class Remaps:
    "Regex-derived aliases for budget categories."

    data: dict[Pattern, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        return cls(data={compile(k): v for k, v in data.items()})

    def get(self, key: str, default: str | None = None) -> str:
        for regex, canonical in self.data.items():
            if regex.search(key):
                return canonical
        return key if not default else default


@dataclass
class Config:
    currencies: list[str]
    regexes: Regexes
    paths: Paths
    remaps: Remaps

    @classmethod
    def from_file(cls, path) -> Self:
        with open(path, mode="rb") as f:
            data = tomllib.load(f)

        return cls(
            currencies=data["currencies"],
            regexes=Regexes.from_dict(data["regexes"]),
            paths=Paths.from_dict(data["paths"]),
            remaps=Remaps.from_dict(data.get("remaps", {})),
        )

    @staticmethod
    def write_example(path) -> None:
        with open(path, mode="w", encoding="utf-8") as f:
            f.write(EXAMPLE)

    @property
    def default_currency(self) -> str:
        return self.currencies[0]


EXAMPLE = """# All keys are required.

# Currencies with which to budget, the default being first.
# Most people will budget with one currency and perhaps track
# vacation time. International workers might budget with
# multiple currencies, e.g., USD and MXN.
currencies = ["USD", "VACHR"]

[regexes]
# Your cash accounts. Include vacation accounts if you budget such time.
cash =  "^Assets:(Cash:(Bank1|Bank2)|TimeOff):"

# Deductions from your paycheck. Money taken before
# it arrives at the bank can't be budgeted with,
# so these categories are excluded from the budget.
# Tax refunds, if applicable, should be categorized
# as income, e.g., `Income:Tax`.
deductions = "^Expenses:(Taxes|Health:Insurance):"

# Catch-alls for their respective categories,
# used in calculating budget balances.
expenses = "^Expenses:"
income = "^Income:"
credit = "^Liabilities:Bank:CreditCard"
loans = "^Liabilities:Bank:Mortgage"
transfers = "^Equity:Transfers$"

# Your investment accounts, so you can budget for moving money
# from a cash account to one of these.
invest = "^Assets:Invest:(Brokerage1|Brokerage2)"

# Opening balances count as net income.
open = "^Equity:Open$"

[paths]
# Your main Beancount file, i.e., the one you provide
# when launching Fava or using `bean-*` commands.
beancount = "main.beancount"

# These are directories. `beancount_budget` will create files inside
# for each currency, e.g., `budgets/USD.csv`.
budgets = "budgets"
quotas = "quotas"

[remaps]
# Remaps will map Beancount accounts to abstract categories.
# The target category need not be an existing Beancount account.
# For example:
# "Mortgage:.*" = "Expenses:Mortgage"
"""
