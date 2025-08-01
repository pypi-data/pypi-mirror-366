from click.testing import CliRunner
from pytest import raises

from beancount_budget.budget import Budget
from beancount_budget.cli import add, configure, fill, reinit, show, sub, trim
from beancount_budget.config import EXAMPLE

from . import ARBITRARY_CATEGORY, LAST_MONTH, config, takes_data_dir


def check_output(result, path):
    assert result.exit_code == 0
    with open(path) as f:
        assert result.output == f.read()


@takes_data_dir
def test_show_options(datafiles):
    runner = CliRunner()
    obj = {"config": config(datafiles)}

    # Reduced depth: `-d 1`
    check_output(
        runner.invoke(show, [str(LAST_MONTH - 1), "-d", "1"], obj=obj),
        datafiles / "outputs" / "test_show_reduced_depth.txt",
    )

    # Filters: `-f {surplus,overspent}`
    check_output(
        runner.invoke(show, [str(LAST_MONTH - 1), "-f", "surplus"], obj=obj),
        datafiles / "outputs" / "test_show_filtered.txt",
    )
    check_output(
        runner.invoke(show, [str(LAST_MONTH - 1), "-f", "overspent"], obj=obj),
        datafiles / "outputs" / "test_show_filtered.txt",
    )


@takes_data_dir
def test_show_everything(datafiles):
    runner = CliRunner()
    obj = {"config": config(datafiles)}

    check_output(
        runner.invoke(show, ["-A", "-f", "all"], obj=obj),
        datafiles / "outputs" / "test_show_everything.txt",
    )


@takes_data_dir
def test_configure(datafiles):
    runner = CliRunner()
    path = datafiles / "config.toml"
    obj = {"path": path}

    result = runner.invoke(configure, obj=obj)

    assert result.exit_code == 0
    with open(path) as f:
        assert f.read() == EXAMPLE


@takes_data_dir
def test_configure_does_not_overwrite(datafiles):
    runner = CliRunner()
    path = datafiles / "bcbudget.toml"
    obj = {"path": path}

    result = runner.invoke(configure, obj=obj)

    assert result.exit_code == 2
    with open(path) as f:
        assert f.read() != EXAMPLE


@takes_data_dir
def test_fill_output(datafiles):
    runner = CliRunner()
    obj = {
        "config": config(datafiles, beancount="total_shortfall.beancount"),
    }

    check_output(
        runner.invoke(fill, [str(LAST_MONTH)], obj=obj),
        datafiles / "outputs" / "test_fill_output.txt",
    )


@takes_data_dir
def test_reinit(datafiles):
    runner = CliRunner()
    obj = {"config": config(datafiles)}

    check_output(
        runner.invoke(reinit, ["-f"], obj=obj),
        datafiles / "outputs" / "test_reinit.txt",
    )


@takes_data_dir
def test_cli_moves(datafiles):
    runner = CliRunner()
    obj = {"config": config(datafiles)}

    check_output(
        runner.invoke(add, [ARBITRARY_CATEGORY, "100", str(LAST_MONTH)], obj=obj),
        datafiles / "outputs" / "test_cli_moves_add.txt",
    )

    check_output(
        runner.invoke(sub, [ARBITRARY_CATEGORY, "100", str(LAST_MONTH)], obj=obj),
        datafiles / "outputs" / "test_cli_moves_sub.txt",
    )


@takes_data_dir
def test_trim(datafiles):
    runner = CliRunner()
    obj = {"config": config(datafiles)}

    result = runner.invoke(trim, [str(LAST_MONTH)], obj=obj)
    assert result.stdout == "\n"  # no-op: nothing to trim

    with raises(RuntimeError, match="Records end before the requested month"):
        runner.invoke(trim, [str(LAST_MONTH + 2)], obj=obj, catch_exceptions=False)
