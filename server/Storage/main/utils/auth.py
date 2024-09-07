import os
import requests


def validate_auth(Token):
    try:
        auth_url = os.getenv("AUTH_SERVER_URL")
        req = requests.get(
            f"{auth_url}/validate-auth", headers={"Authorization": f"Token {Token}"}
        )
        res = req.json()
        return res
    except Exception as e:
        return {"data": None, "err": {"msg":"something went wrong"}}
