import requests
import base64
import datetime


class AstraMpesa:
    def __init__(self, consumer_key, consumer_secret, shortcode, passkey, callback_url):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.shortcode = shortcode
        self.passkey = passkey
        self.callback_url = callback_url
        self.token = self._get_access_token()

    def _get_access_token(self):
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        res = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
        res.raise_for_status()
        return res.json()["access_token"]

    def pay(self, phone, amount, account_reference="AstraPay", description="Payment"):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((self.shortcode + self.passkey + timestamp).encode()).decode()

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": description
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        res = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers
        )

        try:
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError:
            return {
                "status": "error",
                "status_code": res.status_code,
                "response": res.text
            }
