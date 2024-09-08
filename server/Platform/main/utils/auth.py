import requests
import os
from .genRes import generateResponse

auth_server_url = os.getenv("AUTH_SERVER_URL")


def validate_auth(token):
    try:
        req = requests.get(
            f"{auth_server_url}validate-auth",
            headers={"Authorization": f"Token {token}"},
        )
        res = req.json()
        return res
    except Exception as e:
        return generateResponse(err={"msg": "something went wrong"})


def get_user_public_id(token):
    try:
        req = requests.get(
            auth_server_url,
            headers={"Authorization": f"Token {token}"},
        )
        res = req.json()
        data = res.get("data", None)
        err = res.get("err", None)
        if err:
            return res
        return generateResponse({"msg": data["profile"]["public_id"]})
    except Exception as e:
        return generateResponse(err={"msg": "something went wrong"})
