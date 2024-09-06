import os
import boto3
import datetime


class CloudStorage:
    def __init__(self, folder="news"):
        self.folder = folder
        self.bucket_name = "ruffle-1"
        self.cloud = boto3.client("s3", os.getenv("AWS_REGION_NAME"))

    def upload(self, file):
        try:
            content_type = file.content_type
            cur_date = datetime.datetime.now()
            key = f"{self.folder}/{cur_date.microsecond}-{file._name}"
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"

            upload = self.cloud.upload_fileobj(
                file, self.bucket_name, key, ExtraArgs={"ContentType": content_type}
            )

            res = {
                "key": key,
                "url": url,
                "content_type": content_type,
            }
            return res
        except Exception as e:
            print(e)
            raise e

    def delete(self, key):
        try:
            self.cloud.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            return False

    def multiple_upload(self, files):
        result = []
        for file in files:
            first = self.upload(file)
            result.append(first)
        return result

    def multiple_delete(self, keys):
        result = []
        for key in keys:
            first = self.delete(key)
        return "done"

    def update(self, key, file):
        is_deleted = self.delete(key)
        if not is_deleted:
            return False
        result = self.upload(file)
        return result
