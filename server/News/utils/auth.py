import requests
import os
from .genRes import generateResponse


class Authorize:
    """
    > This authorization class is only for publisher performing the CUD operations
    """

    def __init__(self, token):
        self.token = token
        self.AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL")
        self.PLATFORM_SERVER_URL = os.getenv("PLATFORM_SERVER_URL")

    def get_user_public_id(self):
        """
        > This method returns the authenticated user public_id if no error is encountered
        """
        try:
            first_req = requests.get(
                f"{self.AUTH_SERVER_URL}public-id",
                headers={"Authorization": f"Token {self.token}"},
            )
            first_res = first_req.json()
            first_detail = first_res.get("detail", None)
            first_data = first_res.get("data", None)
            first_err = first_res.get("err", None)
            if first_detail:
                return {"data": None, "err": {"msg": first_detail}}
            elif first_err:
                return first_res
            return generateResponse({"msg": first_data["msg"]})
        except Exception as e:
            return generateResponse(err={"msg": "something went wrong"})

    def get_publisher_details(self, user_public_id):
        """
        > This method returns the publisher details if no error occurs
        """
        try:
            first = requests.get(
                f"{self.PLATFORM_SERVER_URL}publisher/single?id={user_public_id}"
            )
            second = first.json()
            return second
        except Exception as e:

            return generateResponse(err={"msg": "something went wrong."})

    def is_admin_publisher(self):
        try:
            first = self.get_user_public_id()
            if first["err"]:
                return first
            user_public_id = first["data"]["msg"]
            second = self.get_publisher_details(user_public_id)
            if second["err"]:
                return second
            is_admin = second["data"]["msg"]["is_admin"]
            return generateResponse({"msg": is_admin})
        except Exception as e:
      
            return generateResponse(err={"msg": "something went wrong"})

    def is_publisher(self):
        try:
            first = self.get_user_public_id()
            if first["err"]:
                return first
            user_public_id = first["data"]["msg"]
            second = self.get_publisher_details(user_public_id)
            return second
        except Exception as e:
   
            return generateResponse(err={"msg": "something went wrong"})
