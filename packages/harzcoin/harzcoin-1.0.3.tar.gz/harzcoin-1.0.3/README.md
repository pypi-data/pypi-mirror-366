# 🪙 Harzcoin

**Harzcoin** is a totally real, completely serious crypto library built for the HarsizStudios ecosystem. This wrapper makes it stupidly easy to interact with the Harzcoin API — sending coins, viewing wallets, and creating new ones.

---

## 🚀 Features

- 🔐 Create wallets
- 💸 Send $HARZ to other wallets
- 👀 View wallet balances and transaction history
- 🔁 Automatically calculates transaction fees

---

## 📦 Installation

```bash
pip install harzcoin
```
🧠 Usage

import harzcoin

# Check version
harzcoin.version()  # shows Harzcoin + API version

# Create a wallet
wallet = harzcoin.create_wallet()
print(wallet)

# View a wallet
info = harzcoin.view_wallet("hz1234567")
print(info)

# Send $HARZ
tx = harzcoin.send(
    wallet_id="hz1111111",
    wallet_key="abc-xyz-123",
    receiver_id="hz2222222",
    amount=10,
    fees_wallet="hz0000001"
)
print(tx)
📘 API Reference
harzcoin.version(type: str = "harzcoin")
Prints the version of either the Harzcoin client or the API.

harzcoin.create_wallet() -> dict
Creates a new wallet.

Returns:

{
  "success": True,
  "transactionId": "...",
  "message": "Transaction completed successfully"
}
harzcoin.view_wallet(wallet_id: str) -> dict
Fetches wallet balance + recent transactions.

harzcoin.send(wallet_id, wallet_key, receiver_id, amount, fees_wallet) -> dict
Sends $HARZ from one wallet to another.

Handles fee calculation automatically.

❗ Notes
Transactions include a 5% fee taken by fees_wallet.

If the fee is less than 2.5 HARZ, the transaction is rejected.

This library just wraps around a Supabase-powered API.

🧪 Version Info
Harzcoin Library: v2.0.6+

API Version: v1.0.1-

📄 License
MIT License. Go nuts.

✨ Made by Harsiz
Not financial advice. Definitely not a scam. Definitely.