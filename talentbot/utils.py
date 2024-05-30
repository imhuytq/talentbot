import boto3

from talentbot.constants import BUCKET_NAME


def generate_signed_url(file, expiration=3600):
    s3_client = boto3.client("s3")
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": file},
            ExpiresIn=expiration,
        )
        return response
    except Exception:
        return None
