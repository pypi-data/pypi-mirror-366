from collections.abc import Callable
from decimal import Decimal

from beancount_budget.budget import Budget
from beancount_budget.month import Month
from beancount_budget.quota.types import Quota

from . import LAST_MONTH, ZERO, config, takes_data_dir


@takes_data_dir
def test_quotas(datafiles):
    b = Budget.from_config(config(datafiles))
    month = LAST_MONTH

    b.reinit()
    b.fill(month)

    # First month's quota is budgeted twice: once to pay for
    # that month's tram, and once to keep the balance at $120.
    assert b[b.months[0]]["Expenses:Transport:Tram"] == Decimal(240)

    # Balance is already $120 and new month has no tram ticket purchases,
    # so no budgeting needed here.
    assert b[b.months[-1]]["Expenses:Transport:Tram"] == ZERO

    # The bank fee is covered by a fixed quota: no required balance,
    # only a required _budgeted_ amount.
    assert (
        b[b.months[0]]["Expenses:Financial:Fees"]
        == b[b.months[-1]]["Expenses:Financial:Fees"]
        == Decimal(4)
    )


def test_required_balances():
    def check(qdata: dict, month: Month, expected: Decimal | None):
        assert Quota.from_dict(qdata).required_balance(month) == expected

    quota = {
        "yearly": {"month": 1},
        "amount": 1200,
    }

    check(quota, Month(2000, 4), Decimal(400))
    check(quota, Month(2024, 12), Decimal(1200))

    quota = {
        "goal": {"by": "2024-01", "hold": True},
        "amount": 1200,
        "start": "2023-01",
    }

    check(quota, Month(2023, 4), Decimal(400))
    check(quota, Month(2022, 12), None)
    check(quota, Month(2024, 1), Decimal(1200))
    check(quota, Month(2024, 2), Decimal(1200))

    quota["goal"]["hold"] = False
    check(quota, Month(2024, 2), Decimal(0))
    quota["goal"]["hold"] = "2024-02"
    check(quota, Month(2024, 2), Decimal(0))
    quota["goal"]["hold"] = "2024-06"
    check(quota, Month(2024, 2), Decimal(1200))


def test_quantization():

    def check(quantize: Callable[[Decimal], Decimal], expected: str):
        quota = Quota.from_dict(
            {
                "yearly": {"month": 1},
                "amount": 1200,
            },
            quantize=quantize,
        )
        assert str(quota.required_balance(Month(2024, 2))) == expected

    check(lambda x: x.quantize(Decimal("0")), "200")
    check(lambda x: x.quantize(Decimal("0.00")), "200.00")
    check(lambda x: x.quantize(Decimal("0.0000")), "200.0000")
