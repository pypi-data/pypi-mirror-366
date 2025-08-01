
# Payra Python SDK (Backend Signature Generation)

This Python SDK provides backend functionality to **generate and verify payment signatures** for the [Payra](https://payra.cash) on-chain payment system.  
It allows your server to securely sign payment requests using an Ethereum private key, without any connection to the blockchain.

## How It Works

Typical flow:

1. The **frontend** prepares all required payment parameters:
   - Network (name: e.g. Polygon, Linea, etc.)
   - Token address
   - Order ID
   - Amount (already in smallest unit — e.g., wei or 10⁶)
   - Timestamp
   - Payer wallet address
3. The frontend sends these parameters to your backend.
4. The **backend** uses this SDK to generate a cryptographic signature using its private key (offline).
5. The signature is returned to the frontend.
6. The frontend calls the Payra smart contract (`payOrder`) using those parameters + the signature.

This ensures full compatibility between your backend and Payra’s on-chain logic.

---

## Features

- ABI encoding of parameters (token, merchantId, orderId, amount, timestamp, payer)
- Keccak256 hashing (same as `ethers.utils.keccak256`)
- Ethereum ECDSA signing of raw hashes (no prefixing)
- Offline signature verification (recover signer address)
- Supports **multiple networks** via dynamic `.env` configuration

---

## SETUP

Before installing this package, make sure you have an active Payra account:

- [https://payra.cash](https://payra.cash)

You will need your merchantID and a dedicated account (private key) to generate valid payment signatures.

---

## Installation

Installing via PyPI (Python Package Index)

```bash
pip install payra-sdk
```

Clone and install locally (editable mode for development):

```bash
git clone https://github.com/payracash/payra-sdk-python.git
cd payra-sdk-python

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -e .
```

## Environment Configuration

Create a `.env` file in your project root:

```bash
cp .env.example .env
```

Edit the `.env` file and add credentials for each supported network. Example for Polygon:

```bash
PAYRA_POLYGON_PRIVATE_KEY=0xabc123...your_private_key
PAYRA_POLYGON_MERCHANT_ID=3652
```

You can define other networks similarly:

```bash
PAYRA_LINEA_PRIVATE_KEY=0xabc...
PAYRA_LINEA_MERCHANT_ID=999
```

**DO NOT commit your  `.env`  to version control.**

---

## Usage Example

Here’s how to generate and verify a Payra signature in your backend:

```python
from payra_sdk import PayraSignatureGenerator, PayraSDKException

PAYMENT_DATA = {
    "network": "polygon",
    "tokenAddress": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",  # USDT on Polygon
    "orderId": "ORDER-1753824905006-301-322",
    "amount": 4000000,  # e.g., 4 USDT with 6 decimals
    "timestamp": 1753826059,  # current Unix time (in seconds)
    "payerAddress": "0xe6c961D6ad9a27Ea8e5d99e40abaC365DE9Cc162"
}

try:
    # Initialize the signer
    payra_signer = PayraSignatureGenerator()

    # Generate signature
    signature = payra_signer.generate_signature(
        network=PAYMENT_DATA["network"],
        token_address=PAYMENT_DATA["tokenAddress"],
        order_id=PAYMENT_DATA["orderId"],
        amount=PAYMENT_DATA["amount"],
        timestamp=PAYMENT_DATA["timestamp"],
        payer_address=PAYMENT_DATA["payerAddress"]
    )

    print(f"Generated signature: {signature}")

except PayraSDKException as e:
    print(f"Payra SDK error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing
You can run the included `example.py` to test signing and verification:

```python
python3 example.py
```

Make sure your `.env` file contains correct values for the `network` being used.

---

## Projects

-   [GitHub / Home](https://github.com/payracash)
-   [GitHub / Source](https://github.com/payracash/payra-sdk-python)
-   [GitHub / Issues](https://github.com/payracash/payra-sdk-python/issues)

---

## Project

-   [https://payra.cash](https://payra.cash)
-   [https://payra.tech](https://payra.tech)
-   [https://payra.xyz](https://payra.xyz)
-   [https://payra.eth](https://payra.eth)

---

## Social Media

- [Telegram Payra Group](https://t.me/+GhTyJJrd4SMyMDA0)
- [Telegram Announcements](https://t.me/payracash)
- [Twix (X)](https://x.com/PayraCash)

---

##  License

MIT © [Payra](https://github.com/payracash)
