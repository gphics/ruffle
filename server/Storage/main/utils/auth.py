import os
import requests


def validate_auth(token):
    auth_url = os.getenv("AUTH_SERVER_URL")
    req = requests.get(f"{auth_url}/validate-auth", headers={"Authorization": f"Token {token}"})
    res = req.json()
    return res
