# Running project

A small pandas-based data-processing project that cleans sales data, calculates
revenue, and aggregates the result by region. It also provides a reusable
`add_virtual_column` helper for creating a new DataFrame column from an
arithmetic expression.

## Requirements

- Python 3.13 or newer
- [`uv`](https://docs.astral.sh/uv/) (recommended), or Python's built-in
  virtual-environment tools

## Installation

Clone the repository and change into its directory:

```bash
git clone <repository-url>
cd cf-task
```

### Using uv (recommended)

`uv` uses `pyproject.toml` and the committed `uv.lock` file to install the
project dependencies:

```bash
uv sync
```

This installs the runtime dependency (`pandas`) and the development
dependency (`pytest`) into a project virtual environment.

### Using a standard virtual environment

On Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pandas pytest
```

On macOS or Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pandas pytest
```

## Running the data pipeline

The pipeline reads `sales.csv` from the project directory, normalizes the
input, calculates revenue and writes the regional totals to `revenue_by_region.csv`.

With `uv`:

```bash
uv run python pipeline.py
```

With an activated virtual environment:

```bash
python pipeline.py
```

Run the command from the repository root so that the relative input and output
paths resolve correctly. Running the pipeline overwrites
`revenue_by_region.csv`.

## Running the tests

Run the complete test suite with:

```bash
uv run pytest
```

or, with an activated virtual environment:

```bash
pytest
```

The tests cover numeric-column normalization, invalid-row handling, arithmetic
operations, validation of expressions and column names, and protection
against modifying the input DataFrame.

## Using `add_virtual_column`

`add_virtual_column` is defined in `solution.py` and accepts:

1. A pandas `DataFrame`.
2. An arithmetic expression using existing column names.
3. The name of the new column.

Supported expressions use existing column names and arithmetic operators such
as `+`, `-`, `*`, `/`, and `**`. Column names and the new column name may
contain only letters and underscores. Invalid expressions, unknown columns,
unsupported function calls, or invalid names return an empty DataFrame and
print a validation message.

The function returns a copy of the input DataFrame, so the original DataFrame
is not modified.

# Assumptions and decisions for virtual column function

A simple parser for individual expressions could be implemented using a
regular expression. However, such a solution would be significantly limited.
The main difficulty would be handling nested expressions with parentheses and
more complex expressions consisting of multiple operations. For example, an
expression such as:

```text
x * (y + z) - w / 2
```

would require the parser to handle both the order of operations and the
parentheses correctly. A regular expression alone is not well suited to this
task.

For this reason, the built-in `ast` module is used to parse the expression.
The resulting syntax tree is traversed to collect all names occurring in the
expression, and these names are checked against the DataFrame column names.
Because `ast` supports Python expression syntax, this approach allows
expressions that are considerably more complex than a simple sequence of
binary operations.

Instead of manually traversing the expression tree to evaluate every
operation, the implementation uses the built-in `DataFrame.eval()` method.
This delegates expression evaluation to pandas and keeps the implementation
compact.

The function supports the operators that are supported by `DataFrame.eval()`,
including:

- arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, and `**`;
- parentheses for grouping and controlling the order of evaluation.

Function calls such as `sin(value)` or `sqrt(value)` are not supported. In
the current implementation, a function name is collected as a name occurring
in the expression, so validation treats it as a column name. Since it is
normally not a column in the input DataFrame, the expression is rejected.

# Data cleaning and calculating revenues

During the data-cleaning and processing stage, I identified the following
data-quality issues. The guiding principle was to attempt to repair the data
and discard rows only as a last resort:

- A repeated header row appears in the middle of the file. The
  script detects such rows and removes them.
- Some values are surrounded by whitespace, and some numeric values contain
  whitespace inside them. The cleaning function removes this whitespace. For
  example, values such as `1 762` are converted to `1762`.
- Several quantity values appear to be outliers, for example `1 762`,
  `1 745`, `1 371`, and `1 427`. It would be reasonable to reject these
  records, but I decided to retain them because they may represent valid
  large orders.
- Some `Quantity` values are negative, even though negative quantities do not
  make sense in this context. Rather than discarding these rows, I treated
  the values as data-entry errors and converted them to their absolute values.
  There are six such values in the source file: `-2`, `-4`, `-5`, `-3`,
  `-3`, and `-2`.
- Some floating-point values use a comma as the decimal separator. The script
  treats this as a formatting error and converts the values to the
  dot-separated format. Seven `Unit Price` values use this notation, for
  example `59,00` and `39,90`.
- The final row contains aggregate values rather than a real
  transaction. It is therefore removed before processing.
- `Region` values are stripped of surrounding whitespace and normalized to a
  consistent capitalization using `capitalize()`. The source contains
  variants such as `west  `, ` South`, `south`, and `EAST`; these are
  normalized to `West`, `South`, and `East`.
- Column names are normalized to the format accepted by
  `add_virtual_column`: spaces are replaced with underscores. For example,
  `Order ID` becomes `Order_ID` and `Unit Price` becomes `Unit_Price`.
- Empty values in the `Discount` column are replaced with `0` so that the
  column can be used safely by `add_virtual_column`.
- There are eb empty rows in the `Unit Price` column. Under the current cleaning strategy these
empty numeric values are converted to `0`, rather than causing the rows to be
discarded. This is an explicit consequence of treating missing numeric values
as zero and should be considered when interpreting the calculated revenue.

