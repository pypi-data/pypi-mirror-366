__version__ = "1.0.3"
__doc__ = "Harzcoin - the totally serious crypto library"

import requests

BASE_URL = "https://wnafumlmiulybbkqauew.supabase.co/functions/v1"

def version(type: str = "harzcoin"):
    """Prints the version of Harzcoin or its API."""
    if type.lower() == "harzcoin":
        print("v2.0.6+")
    elif type.lower() == "api":
        print(f"{__version__}-")
    else:
        raise ValueError("Invalid type. Choose either 'harzcoin' or 'api'.")

def fetch_wallet(wallet_id: str) -> dict:
    """Fetch info about a Harzcoin wallet."""
    url = f"{BASE_URL}/wallet-view"
    response = requests.post(url, json={"walletId": wallet_id})
    response.raise_for_status()
    return response.json()

def create_wallet() -> dict:
    """Create a new Harzcoin wallet."""
    url = f"{BASE_URL}/create"
    response = requests.post(url)
    response.raise_for_status()
    return response.json()

def send_harz(wallet_id: str, wallet_key: str, receiver_id: str, amount: float, fees_wallet: str) -> dict:
    """Send $HARZ to another wallet."""
    if amount < 2.5:
        raise ValueError("Minimum transfer amount is 2.50 HARZ")

    payload = {
        "walletId": wallet_id,
        "walletKey": wallet_key,
        "receiverId": receiver_id,
        "balanceSending": amount,
        "feesWallet": fees_wallet
    }

    url = f"{BASE_URL}/send"
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()
