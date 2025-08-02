# AstraPay SDK

A lightweight Python SDK for M-Pesa STK Push built by Astra Softwares.

## Installation

```bash
pip install astrapay



``bash
from astrapay import AstraMpesa

client = AstraMpesa(
    consumer_key="YOUR_KEY",
    consumer_secret="YOUR_SECRET",
    shortcode="174379",
    passkey="YOUR_PASSKEY",
    callback_url="https://yourdomain.com/callback"
)

res = client.pay(phone="254712345678", amount=100)
print(res)




---

### 🔹 Step 6: `LICENSE` (MIT)

```txt
MIT License

Copyright (c) 2025 Ishmael Bett

Permission is hereby granted, free of charge, to any person obtaining a copy...

