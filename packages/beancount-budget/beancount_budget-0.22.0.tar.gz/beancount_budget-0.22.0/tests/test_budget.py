from decimal import Decimal

from pytest import raises

from beancount_budget.budget import AVAIL, Budget
from beancount_budget.month import Month

from . import (
    ARBITRARY_CATEGORY,
    DELETED_CATEGORY,
    LAST_MONTH,
    ZERO,
    config,
    default_budget,
    takes_data_dir,
)


@takes_data_dir
def test_budget_stability(datafiles):
    c = config(datafiles)
    b = default_budget(datafiles)

    with open(c.paths.budgets / "USD.csv") as f:
        before = f.read()
    b.reinit()
    b.write()
    with open(c.paths.budgets / "USD.csv") as f:
        after = f.read()

    assert before == after


@takes_data_dir
def test_autoextend(datafiles):
    b = default_budget(datafiles)
    with raises(KeyError):
        # Avoid `B.__getitem__`, which has `@check_bounds`,
        # which calls `B.extend`.
        b.data[ARBITRARY_CATEGORY][LAST_MONTH + 1]
    assert b[LAST_MONTH + 1]

    # Budget data should be stable after a round-trip through disk.
    b.write()
    b = default_budget(datafiles)

    b.format(LAST_MONTH + 1)


@takes_data_dir
def test_out_of_bounds(datafiles):
    b = default_budget(datafiles)
    with raises(RuntimeError, match="Records begin after the requested month"):
        b[Month(2000, 1)]
    with raises(RuntimeError, match="Records end before the requested month"):
        b[Month(2030, 1)]


@takes_data_dir
def test_simple_mutations(datafiles):
    b = default_budget(datafiles)

    def should_be(bal: int, f, amt: int):
        "Should be `bal` after `f(..., amt)`."
        # More legible than writing this out thrice.
        f(LAST_MONTH + 1, ARBITRARY_CATEGORY, Decimal(amt))
        assert b[LAST_MONTH + 1][ARBITRARY_CATEGORY] == Decimal(bal)

    should_be(100, b.add, 100)
    should_be(500, b.set_amt, 500)
    should_be(0, b.sub, 500)


@takes_data_dir
def test_whole_budget_mutations(datafiles):
    b = default_budget(datafiles)
    m = LAST_MONTH + 1
    cat = "Expenses:Transport:Tram"

    b.set_amt(m, cat, Decimal(-120))
    b.fill(m)
    assert b[m][cat] == ZERO

    b.add(m, cat, Decimal(100))
    b.trim(m)
    assert b[m][cat] == ZERO


@takes_data_dir
def test_total_shortfall(datafiles):
    overspent = "Expenses:Food:Groceries"
    c = config(datafiles, beancount="total_shortfall.beancount")
    m = LAST_MONTH

    b = Budget.from_config(c)
    b.fill(m)
    bals = b.balances(m)
    assert b[m][overspent] == Decimal("1609.96")
    assert bals[overspent] == Decimal("-2998390.04")
    assert bals[AVAIL] == ZERO


@takes_data_dir
def test_fill_from_category(datafiles, monkeypatch):
    overbudgeted = "Expenses:Transport:Tram"

    c = config(datafiles, beancount="total_shortfall.beancount")
    m = LAST_MONTH
    with monkeypatch.context() as mp:
        mp.setattr("beancount_budget.budget.fzf", lambda _: overbudgeted)

        b = Budget.from_config(c)
        b.add(m, overbudgeted, 10000)
        b.fill(m)

        # $10120 taken from tram to cover groceries, but B.fill ends
        # with "no money left" before tram balance can be replaced.
        assert b[m][overbudgeted] == Decimal(-120)


@takes_data_dir
def test_dry_fill(datafiles):
    c = config(datafiles, beancount="total_shortfall.beancount")
    m = LAST_MONTH

    b = Budget.from_config(c)
    before = b[m], b.balances(m)
    b.fill(m, dry_run=True)
    assert before == (b[m], b.balances(m))


@takes_data_dir
def test_warn_on_misspelt_quotas(capsys, datafiles):
    c = config(datafiles, quotas="quotas_misspelt")
    _ = Budget.from_config(c).deviations(LAST_MONTH)
    assert "Found mismatched category names" in capsys.readouterr().out


@takes_data_dir
def test_deleted_category(datafiles):
    c = config(datafiles, budgets="budgets_deleted_category")
    b = Budget.from_config(c)

    assert DELETED_CATEGORY in b.categories
    assert b[Month(2022, 1)][DELETED_CATEGORY] == Decimal(10)


@takes_data_dir
def test_reinit_removes_deleted_category(datafiles):
    c = config(datafiles, budgets="budgets_deleted_category")
    b = Budget.from_config(c)

    b.reinit()
    assert b[Month(2022, 1)][DELETED_CATEGORY] == Decimal(0)

    b.write()
    with open(c.paths.budgets / "USD.csv") as f:
        after = f.read()

    assert DELETED_CATEGORY not in after
