# pyinr

A simple Python package to convert Indian Rupees (INR) to other currencies.

## Installation

You can install `pyinr` directly from PyPI using pip:

```bash
pip install pyinr
```

## Usage

Here's how you can use the `pyinr` module to perform currency conversions:

```python
from pyinr import convert

# Example: Convert 100 INR to USD
usd_amount = convert(100, "USD")
print(f"100 INR is equal to {usd_amount} USD")

# Example: Convert 500 INR to EUR
eur_amount = convert(500, "EUR")
print(f"500 INR is equal to {eur_amount} EUR")

# Example: Convert 250 INR to JPY
jpy_amount = convert(250, "JPY")
print(f"250 INR is equal to {jpy_amount} JPY")
```

**Note:** The `convert` function currently uses a fixed exchange rate for demonstration purposes. For real-world applications, you would integrate with a live exchange rate API.

## PyPI Instructions

This package is available on PyPI. You can find it by searching for `pyinr` on the [PyPI website](https://pypi.org/).

To install it, simply run:

```bash
pip install pyinr
```

If you encounter any issues or have suggestions, please report them on the [Bug Tracker](https://github.com/ganeshdatta23/pyinr/issues).