#!/bin/sh

run() {
  (cd tests/data && PYTHONPATH=../..:$PYTHONPATH python -m beancount_budget -c bcbudget.toml "$@")
}

# TODO: the rest
run show -Af all > tests/data/outputs/test_show_everything.txt
