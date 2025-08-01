import sys
from decimal import Decimal
from pathlib import Path

import click

from beancount_budget.budget import Budget, FilterRows
from beancount_budget.config import Config
from beancount_budget.month import Month


class MonthParamType(click.ParamType):
    name = "month"

    def convert(self, value, param, ctx) -> Month:
        return Month.from_str(value)


takes_currency = click.option("-x", "--currency", default=None)
takes_month = click.argument("month", type=MonthParamType(), default=str(Month.this()))


@click.group()
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    default=".bcbudget.toml",
    show_default=True,
)
@click.pass_context
def main(ctx, config_path) -> None:  # pragma: no cover
    "An envelope-budgeter powered by Beancount."

    ctx.ensure_object(dict)

    if ctx.invoked_subcommand == "configure":
        # Click will hand off to configure().
        ctx.obj["path"] = config_path
    elif config_path.exists():
        ctx.obj["config"] = Config.from_file(config_path)
    else:
        suggestion = (
            "configure"
            if ctx.get_parameter_source("config_path")
            == click.core.ParameterSource.DEFAULT
            else f"-c {config_path} configure"
        )
        click.echo(
            f"No configuration found at `{config_path}`.\n"
            f"Run `budget {suggestion}`."
        )
        sys.exit(1)


@main.command()
@click.pass_context
def configure(ctx) -> None:
    "Write starter configuration to disk."
    path = ctx.obj["path"]
    if path.exists():
        raise click.UsageError(f"`{path}` already exists.")

    Config.write_example(path)
    click.echo(
        f"Example configuration written to `{path}`.\n"
        "Use your preferred editor to finish configuration."
    )


@main.command()
@takes_month
@takes_currency
@click.pass_context
def fill(ctx, currency: str, month: Month) -> None:
    "Assign budget amounts automatically."
    budget = Budget.from_config(ctx.obj["config"], currency)
    click.echo(budget.fill(month))
    budget.write()


@main.command()
@takes_currency
@click.option(
    "-f",
    "--force",
    is_flag=True,
    type=bool,
    default=False,
    help="Proceed without asking.",
)
@click.pass_context
def reinit(ctx, currency: str, force: bool) -> None:
    "Clear budget and auto-fill it from first month."
    budget = Budget.from_config(ctx.obj["config"], currency)
    sigil = "Fry my budget, cap'n"

    if not force:  # pragma: no cover
        # fmt: off
        click.echo("\n".join((
            "WARNING: This will clear all data in your budget.",
            "You should make a backup beforehand.",
            "Alternately, keep your budget version-controlled (e.g., in Git).",
        )))
        # fmt: on
        try:
            if click.prompt(f'Type "{sigil}" to confirm: ') != sigil:
                return
        except click.Abort:
            return

    budget.reinit(verbose=True)
    budget.write()


@main.command()
@takes_month
@click.option("-A", "--all-months", is_flag=True, type=bool, default=False)
@click.option(
    "-f",
    "--filter",
    type=click.Choice(list(FilterRows)),
    default=FilterRows.DEFAULT,
    help="Default shows rows with at least one nonzero value.",
)
@click.option("-d", "--depth", type=int, default=None)
@click.option("-o", "--output", type=click.Choice(("table", "csv")), default="table")
@takes_currency
@click.pass_context
def show(
    ctx,
    currency: str,
    month: Month,
    output: str,
    depth: int | None,
    filter: FilterRows,
    all_months: bool,
) -> None:
    "Show budgeted amounts, balances, and quotas."
    budget = Budget.from_config(ctx.obj["config"], currency)
    click.echo(budget.format(month, depth, filter, all_months, output == "csv"))


@main.command()
@click.argument("category")
@click.argument("amount", type=Decimal)
@takes_month
@takes_currency
@click.pass_context
def add(ctx, currency: str, category: str, amount: Decimal, month: Month):
    "Add an amount to a category for this (or the given) month."
    budget = Budget.from_config(ctx.obj["config"], currency)
    click.echo(budget.cli_add(month, category, amount))
    budget.write()


@main.command()
@click.argument("category")
@click.argument("amount", type=Decimal)
@takes_month
@takes_currency
@click.pass_context
def sub(ctx, currency: str, category: str, amount: Decimal, month: Month):
    "Subtract an amount from a category for this (or the given) month."
    budget = Budget.from_config(ctx.obj["config"], currency)
    click.echo(budget.cli_sub(month, category, amount))
    budget.write()


@main.command()
@takes_month
@click.pass_context
@takes_currency
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    type=bool,
    default=False,
    help="Don't write changes to disk.",
)
def trim(ctx, currency: str, month: Month, dry_run: bool):
    "Remove surpluses for this (or the given) month, returning them to Available."
    budget = Budget.from_config(ctx.obj["config"], currency)
    click.echo(budget.trim(month, dry_run=dry_run))
    budget.write()


@main.command()
@takes_month
@click.pass_context
@takes_currency
def quotas(ctx, currency: str, month: Month):
    "Show quotas by category."
    budget = Budget.from_config(ctx.obj["config"], currency)
    click.echo(budget.show_quotas(month))
