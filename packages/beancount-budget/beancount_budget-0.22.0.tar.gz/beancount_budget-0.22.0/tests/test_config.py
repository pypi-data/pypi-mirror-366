from beancount_budget.config import EXAMPLE, Config

from . import config, takes_data_dir


@takes_data_dir
def test_config(datafiles):
    assert config(datafiles).paths.beancount == datafiles / "main.beancount"


@takes_data_dir
def test_example_config(datafiles):
    path = datafiles / "tmp.config"
    Config.write_example(path)
    with open(path) as f:
        assert f.read() == EXAMPLE
