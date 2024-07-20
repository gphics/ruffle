import os
import boto3
from .FileValidator import Main
import datetime


class CloudManager(Main):
    """
    * This class inherits from the fileValidator main class which is responsible for file validation
    * This class is responsible for :
        > file upload
        > file delete
    * The media schema to be saved:
        > url
        > key
        > content_type
    """

    def __init__(self, bucket_name, folder):
        self.client = boto3.client("s3", os.getenv("AWS_REGION_NAME"))
        self.folder = folder
        self.bucket_name = bucket_name

    def upload(self, file):
        """
        * Method for uploading single file
        * Return :
            > url
            > key
            > content_type
        """
        try:
            content_type = file.content_type
            cur_date = datetime.datetime.now()
            key = f"{self.folder}/{cur_date.second}-{cur_date.microsecond}-{file._name}"
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            # size = self.to_mb(file.size)
            upload = self.client.upload_fileobj(
                file, self.bucket_name, key, ExtraArgs={"ContentType": content_type}
            )
            result = {
                "url": url,
                "key": key,
                "content_type": content_type,
                # "size": size,
            }
            return result
        except Exception as e:
            print(e)
            raise e

    def delete(self, key):
        """
        * Method for deleting a file
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
        except Exception as e:
            print(e)
            raise e

    def multiple_upload(self, files):
        """
        * Method for multiple file upload
        """
        result = []
        for file in files:
            first = self.upload(file)
            result.append(first)
        return result

    def multiple_delete(self, keys):
        """
        * method for multiple file delete
        """
        for key in keys:
            self.delete(key)
