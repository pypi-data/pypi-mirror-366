# Beancount Budget

A command-line envelope budgeter.

- No custom transaction types needed: your budget lives in CSV files, and balances are computed from Beancount data.
- Set goals using quotas: budget for regular expenses, future large purchases, and more.

## Getting started

### Requirements

Executables:
- Python 3.11+
- column(1), from util-linux
- fzf

Libraries:
- beancount
- click
- python-dateutil


### Installation

```
pip install beancount-budget
```

### Configuration

`budget` needs to know some things:
- regexes for classifying your Beancount accounts; and
- the paths to your Beancount, budget, and quota files.

Running `budget configure` will write a configuration file to the current directory,
or the directory you specify in `budget -c /path/to/dir configure`.

### Untested use cases

If you

- handle more than one currency in your daily finances,
- have ever had to substantially refactor your Beancount accounts,
- have a stance on investments other than "once the money's in the brokerage, it's left my budget", or
- are anything other than a [U.S. W-2](https://www.irs.gov/forms-pubs/about-form-w-2) laborer,

you are encouraged to try this software and email your experiences to the author.

## Example

First, I need some example Beancount data and a configuration for the budget:

```
$ bean-example --seed 0 --date-birth 2022-01-01 --date-end 2024-01-01 > main.beancount
$ budget configure
Example configuration written to `.bcbudget.toml`.
Use your preferred editor to finish configuration.
$ vi .bcbudget.toml
```

This is what the config file looks like after editing:

```toml
currencies = ["USD", "VACHR"]

[regexes]
cash = "^Assets:US:(BofA:Checking|Hoogle:Vacation)"
deductions = "^Expenses:(Taxes:|Health:.*:Insurance$)"
expenses = "^Expenses:"
income = "^Income:"
transfers = "^$"  # explicitly disable unused regexes
credit = "Liabilities:Credit:"
loans = "^$"
invest = "^(Assets|Income):US:ETrade:"
open = "^Equity:Opening-Balances$"

[paths]
beancount = "main.beancount"
budgets = "budgets"
quotas = "quotas"
```

And here is an empty budget.

```
$ budget show 2022-01
Category                   Budgeted  Expenses  Balances  Deviations
Expenses:Financial:Fees                  4.00     -4.00       -4.00
Expenses:Food:Groceries                219.35   -219.35     -219.35
Expenses:Food:Restaurant               329.62   -329.62     -329.62
Expenses:Home:Electricity               65.00    -65.00     -130.00
Expenses:Home:Internet                  80.14    -80.14     -160.14
Expenses:Home:Phone                     68.36    -68.36      -68.36
Expenses:Home:Rent                    2400.00  -2400.00    -2400.00
Expenses:Transport:Tram                120.00   -120.00     -240.00
Total                                 3286.47  -3286.47    -3551.47
Available                                       6649.63
Net income                                      6649.63
```

In this example, all  `budget` commands that require a month will use
`2022-01`. In daily usage you will likely use commands like `budget show`
unqualified.

#### Figuring income

The example data's first month contains an opening balance for a checking
account ($3948.43), and two paychecks whose net balances are almost evenly
split between the checking account and a 401k account ($1350.60 and $1200.00
respectively).

The budgeter's focus is on everyday spending, so 401k postings aren't counted
as income. That leaves `3948.43 + (1350.60 * 2) = 6649.63`.

#### Filling the budget

`budget fill` allocates money to categories until each has enough balance for
the month's expenses and quotas. It tries to eliminate negative deviations.

```
$ budget fill 2022-01 > /dev/null
$ xsv select 'category,"2022-01"' budgets/USD.csv
category,2022-01
Expenses:Financial:Fees,4.00
Expenses:Food:Groceries,219.35
Expenses:Food:Restaurant,329.62
Expenses:Home:Electricity,65.00
Expenses:Home:Internet,80.14
Expenses:Home:Phone,68.36
Expenses:Home:Rent,2400.00
Expenses:Transport:Tram,120.00
$ budget show 2022-01
Category                   Budgeted  Expenses  Balances  Deviations
Expenses:Financial:Fees        4.00      4.00
Expenses:Food:Groceries      219.35    219.35
Expenses:Food:Restaurant     329.62    329.62
Expenses:Home:Electricity     65.00     65.00
Expenses:Home:Internet        80.14     80.14
Expenses:Home:Phone           68.36     68.36
Expenses:Home:Rent          2400.00   2400.00
Expenses:Transport:Tram      120.00    120.00
Total                       3286.47   3286.47
Available                                       3363.16
Net income                                      6649.63
```

`budget trim` does the opposite: it removes money from overbudgeted categories,
in order to eliminate positive deviations.

```
$ budget add Expenses:Transport:Tram 100 2022-01
Expenses:Transport:Tram  (Balance now)    100.00
                         (Balance added)  100.00
                         [Available]      100.00
$ budget trim 2022-01
[Available]  (Balance now)            3363.16
             (Balance added)           100.00
             Expenses:Transport:Tram   100.00
```

#### Adding quotas

For more on the concept, see "Quotas" below.

Some of these categories cost a fixed amount per month, so it makes sense to
start planning for them. To start, create `quotas/$YOUR_CURRENCY.toml`. (Unlike
budgets, quotas are entirely manually set up.)

```toml
["Expenses:Home:Electricity".this]
amount = 65

["Expenses:Home:Internet".self]
amount = 80

["Expenses:Transport:Tram".wow]
amount = 120
```

The quota names were chosen to reflect their arbitrary nature.
I use `this` in whole-category quotas.

```
$ budget fill 2022-01
Expenses:Home:Electricity  (Balance now)     65.00
                           (Balance added)   65.00
                           [Available]       65.00

Expenses:Home:Internet     (Balance now)     80.00
                           (Balance added)   80.00
                           [Available]       80.00

Expenses:Transport:Tram    (Balance now)    120.00
                           (Balance added)  120.00
                           [Available]      120.00
$ budget show 2022-01
Category                   Budgeted  Expenses  Balances  Deviations
Expenses:Financial:Fees        4.00      4.00
Expenses:Food:Groceries      219.35    219.35
Expenses:Food:Restaurant     329.62    329.62
Expenses:Home:Electricity    130.00     65.00     65.00
Expenses:Home:Internet       160.14     80.14     80.00
Expenses:Home:Phone           68.36     68.36
Expenses:Home:Rent          2400.00   2400.00
Expenses:Transport:Tram      240.00    120.00    120.00
Total                       3551.47   3286.47    265.00
Available                                       3098.16
Net income                                      6649.63
```

## Quotas

Quotas are amounts you intend to budget each month. For example, in United States dollars:

- A goal quota: "I want to save $1200 for a vacation six months from now."
- Another goal quota: "I've already saved $10000 for a car, but I'm still looking for the right one."
- A monthly quota: "My groceries cost $200 per month, give or take."
- Another monthly quota: "I started going to a gym last week, and it'll cost $70 per month."
- A group of monthly quotas: "I give to several NPOs monthly, in these amounts: $20, $10, another $10."
- A fixed quota: "I will budget at least $3600 per month for candles, regardless of spending."
- Another fixed quota: "My rent costs $1300."
- A yearly quota: "My PO box costs $24 per month; I pay $288 each June."

The numbers are _strictly illustrative_ and I will brook no complaints about them.

Each of these quotas are assigned to a Beancount account, such as
`Expenses:Gifts:NPO`. Multiple quotas may be assigned to the same account. If
none are assigned to an account, that account has a default quota of zero
(which conceptually reduces to "no overspending").

A goal or yearly quota expects the balance to be fulfilled during the month
_before_ the stated end date. For example:
- If on January you begin a $1200 goal with July as the target month, the $200
  you budget in June will fulfill the quota.
- If you have a $288 yearly quota payable each June, the $24 you budget in May
  will fulfill the quota.

### Schema

Each quota is assigned a category and a name (both strings), and consists of the following fields, with TOML types in parentheses:

- amount (float): The amount to save.
- start (string, optional): The month to begin saving, in `YYYY-MM` format.
- monthly (dict, optional): Specifies a monthly quota. If no quota type is chosen, this is the default.
  - fixed (bool, optional): Instead of requiring a balance, require a budgeted amount each month.
- yearly (dict, optional): Specifies a yearly quota.
  - month (int, required): The month on which the payment recurs.
- goal (dict, optional): Specifies a goal quota.
  - by (string, required): The month by which to save up, in `YYYY-MM` format.
  - hold (bool or string, optional): Whether to keep the saved balance past the goal month.
    If true, hold indefinitely. If a month in `YYYY-MM` format, stop holding on that month.

### Examples

This is how the aforementioned quotas would look in `quotas/USD.toml`:

```toml
["Expenses:Vacation"."Los Angeles"]
goal = {by = "2019-07"}
start = "2019-01"
amount = 1200  # from January to June, you'll budget $200/m

["Expenses:Basics:Groceries".this]  # "this" is arbitrarily chosen
amount = 200                        # to represent whole-account quotas

["Expenses:Basics:Candles".this]
monthly = {fixed = true}
amount = 3600

["Expenses:Basics:Health".gym]
amount = 70
start = "2019-01"

["Expenses:Gifts:NPO"."Department of Redundancy Department"]
monthly = {}  # example of explicitly defining monthly quota
amount = 20

["Expenses:Gifts:NPO"."Benevolent and Proactive Order of Llamas"]
amount = 10

["Expenses:Gifts:NPO"."Feed the Childrens"]
amount = 10

["Expenses:Goals:Car".this]
goal = {by = "2019-01", hold = true}
type = "goal"
start = "2018-01"
amount = 10000

["Expenses:Subs:USPS".this]
yearly = {month = 6}
amount = 288  # = $24/m
```

## Remaps

If you wish to track multiple categories as one line item, you can combine them using a remap.

This remap will map all categories [containing](https://docs.python.org/3/library/re.html#re.search)
the regex `Mortgage:.*` to the abstract category `Expenses:Mortgage`:

```toml
[remaps]
"Mortgage:.*" = "Expenses:Mortgage"
```

The category need not exist in the Beancount data; in this example, there is no
[`open`](https://beancount.github.io/docs/api_reference/beancount.core.html#beancount.core.data.Open)
directive for `Expenses:Mortgage`.

## Further reading
- [YNAB's four rules](https://www.ynab.com/the-four-rules)
