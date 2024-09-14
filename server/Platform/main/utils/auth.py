import requests
import os
from .genRes import generateResponse

auth_server_url = os.getenv("AUTH_SERVER_URL")


def validate_auth(token):
    """
    > This method helps to validate user authentication and returns the appropriate boolean value
    """
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
    """
    > This method is responsible for returning user public_id
    """
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
        return generateResponse({"msg": data["msg"]["public_id"]})
    except Exception as e:
        return generateResponse(err={"msg": "something went wrong"})


def verify_user(public_id):
    """
    > This method helps to verify user from the provided user public_id
    """
    try:
        url = f"{auth_server_url}verify-user?id={public_id}"
        req = requests.get(url)
        res = req.json()
        return res
    except Exception as e:

        return generateResponse(err={"msg": "something went wrong"})