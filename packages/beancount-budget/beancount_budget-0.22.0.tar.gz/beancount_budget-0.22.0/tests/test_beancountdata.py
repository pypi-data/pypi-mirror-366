from decimal import Decimal

from beancount.core.inventory import Inventory

from beancount_budget.beancount import BeancountData
from beancount_budget.month import Month

from . import config, takes_data_dir


@takes_data_dir
def test_net_income(datafiles):
    c = config(datafiles)
    bcd = BeancountData(c.paths.beancount, c.regexes)

    open_bal = Inventory.from_string("3948.43 USD")
    paychecks = Inventory.from_string("1350.60 USD, 5 VACHR") * Decimal(2)

    assert bcd.net_income[Month(2022, 1)] == (open_bal + paychecks)
    assert bcd.net_income[Month(2022, 2)] == paychecks


@takes_data_dir
def test_data_with_errors(datafiles):
    c = config(
        datafiles,
        beancount="txn_error.beancount",
    )
    bcd = BeancountData(c.paths.beancount, c.regexes)

    assert bcd.errors[0].message == "Transaction does not balance: (3948.43 USD)"
    assert len(bcd.errors) == 1
