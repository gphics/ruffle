import boto3
import os
import datetime

s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION_NAME"))
s3 = boto3.resource("s3")


def create_bucket(name):
    try:

        s3_client.create_bucket(Bucket=name)
        print("bucket created`")
    except Exception as e:
        print(e)


def my_bucket():
    res = s3_client.list_buckets()
    print(res["Buckets"])


def upload(file, bucket):
    try:
        ms = datetime.datetime.now().microsecond
        x = s3.upload_file(
            file, bucket, f"rock/fushs-{ms}.jpg", ExtraArgs={"ContentType": "image/jpg"}
        )
        print(x)
    except Exception as e:
        print(e)


def del_file(bucket, key):
    s3.Object(bucket, key).delete()


# del_file("tester-2", "rock/fushs-580970.jpg")
# upload("Feed-master.jpg", "tester-2")
# print(s3.__dict__)
# create_bucket("tester-2")
