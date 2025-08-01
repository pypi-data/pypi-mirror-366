from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from beancount.scripts.example import write_example_file as bean_example  # type: ignore

from beancount_budget.budget import Budget
from beancount_budget.config import Config, Paths
from beancount_budget.month import Month

ZERO = Decimal("0.00")
LAST_MONTH = Month(2024, 4)
ARBITRARY_CATEGORY = "Expenses:Home:Internet"
DELETED_CATEGORY = "Expenses:Transport:Bus"

data_dir = Path(__file__).parent.resolve() / "data"
takes_data_dir = pytest.mark.datafiles(data_dir)


def config(
    data_dir, beancount="main.beancount", budgets="budgets", quotas="quotas"
) -> Config:
    ret = Config.from_file(data_dir / "bcbudget.toml")
    ret.paths = Paths(
        beancount=data_dir / beancount,
        budgets=data_dir / budgets,
        quotas=data_dir / quotas,
    )
    return ret


def default_budget(datafiles) -> Budget:
    c = config(datafiles)
    return Budget.from_config(
        c,
        c.default_currency,
    )
