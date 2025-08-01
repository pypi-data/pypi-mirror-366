from textwrap import dedent

from beancount_budget.budget import Budget

from . import LAST_MONTH, config, takes_data_dir


@takes_data_dir
def test_moves_format(datafiles):
    c = config(datafiles, beancount="total_shortfall.beancount")
    m = LAST_MONTH

    b = Budget.from_config(c)
    moves = b.fill(m)

    assert (
        str(moves)
        == dedent(
            """
        Expenses:Food:Groceries  (Balance now)    -2998390.04
                                 (Balance added)      1609.96
                                 [Available]          1609.96
        """
        ).strip()
    )
