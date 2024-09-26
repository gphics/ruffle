import os
import requests
from .genRes import generateResponse


class Cloud:

    def __init__(self):
        self.cloud_url = STORAGE_SERVER_URL = os.getenv("STORAGE_SERVER_URL")

    def upload(self, media, token):
        try:
            upload = requests.post(
                f"{self.cloud_url}?folder=news",
                files={"media": media},
                headers={"Token": token},
            )
            upload_res = upload.json()
            return upload_res
        except Exception as e:
            return generateResponse(err={"msg": "something went wrong"})

    def delete(self, media_id, token):
        try:

            first = requests.delete(
                f"{self.cloud_url}?id={media_id}", headers={"Token": token}
            )
            second = first.json()
            return second
        except Exception as e:
            return generateResponse(err={"msg": "something went wrong"})

    def batch_delete(self, media_list, token):
        result = None
        err = None
        for media_id in media_list:
            first = self.delete(media_id, token)
            if first["err"]:
                err = first
                break
            result = first
        return result

    def retrieve(self, public_id):
        try:
            first = requests.get(f"{self.cloud_url}?id={public_id}")
            second = first.json()
            return second
        except Exception as e:
            return generateResponse(err={"msg": "something went wrong"})

    def batch_retrieve(self, media_list):
        result = []
        err = None
        for x in media_list:
            first = self.retrieve(x)
            if not first["err"]:
                result.append(first["data"]["msg"])
            else:
                err = first
                break
        if err:
            return err
        return generateResponse({"msg": result})
