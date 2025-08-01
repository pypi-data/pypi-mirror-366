import subprocess
from collections.abc import Collection, Iterable, Sequence
from typing import Any

import click


def fzf(data: Collection[str]) -> str:  # pragma: no cover
    "Run a fuzzy search and return the result."
    data = "\n".join(data)
    # fmt: off
    return subprocess.run(
        ["fzf", "--height=10", "--print-query"],
        input=bytes(data, encoding="utf-8"),
        check=False,
        stdout=subprocess.PIPE,
    ).stdout.decode().strip().split("\n")[-1]
    # fmt: on


def list_problems(problem: str, items: Iterable):
    "Print a list of user-facing warnings."
    lines = (problem, *(f"- {i}" for i in items))
    click.echo("\n".join(lines))


def format_table(
    table: Sequence[Sequence[Any]],
    headers: Sequence[str],
    numerical_headers: Sequence[str],
    csv: bool = False,
) -> str:
    "Format a two-dimensional array into a string."

    def to_str(v: Any) -> str:
        "Turns zeros and Nones into blanks, unlike `str(v)`."
        return str(v) if v else ""

    ret = "\n".join(",".join(to_str(v) for v in row) for row in table)

    if not csv:
        # fmt: off
        ret = subprocess.run(
            [
                "column",
                "--table",
                "--table-noheadings",
                "--separator", ",",
                "--table-columns", ",".join(headers),
                "--table-right", ",".join(numerical_headers),
            ],
            input=bytes(ret, encoding="utf-8"),
            stdout=subprocess.PIPE,
            check=True,
        ).stdout.decode().strip()
        # fmt: on

    return ret
