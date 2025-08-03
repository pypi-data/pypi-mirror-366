import requests


def get_rates(base_currency):
    """Fetches the latest exchange rates for a given base currency."""
    API_URL = f"https://api.exchangerate-api.com/v4/latest/{base_currency.upper()}"
    response = requests.get(API_URL)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()['rates']

def convert(amount, from_currency, to_currency):
    """Converts an amount from one currency to another."""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    rates = get_rates(from_currency)

    if to_currency not in rates:
        raise ValueError(f"Invalid target currency: {to_currency}")

    return amount * rates[to_currency]