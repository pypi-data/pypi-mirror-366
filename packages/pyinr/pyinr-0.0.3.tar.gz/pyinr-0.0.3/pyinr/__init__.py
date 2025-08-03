import requests

API_URL = "https://api.exchangerate-api.com/v4/latest/INR"

def get_rates():
    """Fetches the latest exchange rates."""
    response = requests.get(API_URL)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()['rates']

def convert(inr_amount, to_currency):
    """Converts INR to a target currency."""
    rates = get_rates()
    to_currency = to_currency.upper()
    if to_currency not in rates:
        raise ValueError(f"Invalid currency: {to_currency}")
    return inr_amount * rates[to_currency]