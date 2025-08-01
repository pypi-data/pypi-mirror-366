from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable
from copy import deepcopy
from decimal import Decimal
from typing import Any

import click

from beancount_budget.beancount import PerCategory
from beancount_budget.month import Month
from beancount_budget.moves import Moves

AVAIL = "[Available]"


def set_difference(s1: Iterable[Hashable], s2: Iterable[Hashable]) -> set:
    "Return elements in s1 not present in s2."
    return set(s1) - set(s2)


def get_by_depth(data: PerCategory[Decimal], depth: int) -> PerCategory[Decimal]:
    "Compress given data (assumed to be keyed by category) like `hledger --depth`."
    ret: dict = defaultdict(Decimal)
    for k, v in data.items():
        parts = k.split(":")[:depth]
        ret[":".join(parts)] += v
    return ret


def check_bounds(f: Callable) -> Callable:
    """Ensure a request falls within the budget's timespan.
    The callable's first argument must be a `Month`.
    """

    def wrapper(self, month, *args, **kwargs) -> Any:
        if month < self.months[0]:
            raise RuntimeError(f"Records begin after the requested month ({month}).")

        if month - 1 == self.months[-1]:
            # This usually means the user has run a `budget` command
            # before importing transactions for the current month.
            click.echo(
                f"NOTE: Requested month ({month}) is one after budget's last.\n"
                "Budget auto-extended."
            )
            self.extend(month)

        elif month > self.months[-1]:
            raise RuntimeError(f"Records end before the requested month ({month}).")

        return f(self, month, *args, **kwargs)

    return wrapper


def track_moves(f: Callable) -> Callable:
    """Track and summarize whole-budget mutations.

    The callable's signature must contain `self` and a `Month`,
    and the return type must be `Moves`. A `bool` argument
    (of which there must be at most one) will be interpreted
    as the switch for a dry run.
    """

    def wrapper(self, *args, **kwargs) -> Moves:
        moves = f(self, *args, **kwargs)

        # Fish in args for needed values.
        if not (month := kwargs.get("month")):
            if not (month := next(a for a in args if isinstance(a, Month))):
                raise ValueError(
                    "Move-tracked Budget method called without Month arg."
                )  # pragma: no cover

        if not (dry_run := kwargs.get("dry_run")):
            bools = [a for a in args if isinstance(a, bool)]
            if len(bools) > 1:
                raise ValueError(
                    "Move-tracked Budget method called with too many Booleans."
                )  # pragma: no cover
            dry_run = any(bools)

        # Commit moves to budget.
        b = self if not dry_run else deepcopy(self)
        for to_acct, move in moves.data.items():
            for from_acct, amt in move.items():
                if from_acct != AVAIL:
                    b.sub(month, from_acct, amt)
                if to_acct != AVAIL:
                    b.add(month, to_acct, amt)

        return moves

    return wrapper
