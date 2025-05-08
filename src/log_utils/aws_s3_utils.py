import logging
from urllib.parse import urlparse

import boto3
import streamlit as st
from botocore.exceptions import ClientError


@st.cache_data(ttl=3600)
def create_presigned_url(
    bucket_name: str, object_name: str, expiration: int = 3600
) -> str | None:
    """Generate a presigned URL to share an S3 object.

    Args:
        bucket_name (str): The name of the S3 bucket
        object_name (str): The name of the S3 object
        expiration (int): The time in seconds for the presigned URL to remain valid

    Returns:
        str: The presigned URL as a string. If error, returns None.

    """
    s3_client = boto3.client("s3")
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


@st.cache_data
def parse_s3_url_for_presigned_url(s3_url: str) -> tuple[str, str]:
    """Parse an S3 URL and return the bucket name and object name.

    Note that the object name is transformed from the dashboard JSON path to the eval zip path.

    Args:
        s3_url (str): The S3 URL to parse

    Returns:
        tuple[str, str]: The bucket name and object name

    """
    o = urlparse(s3_url, allow_fragments=False)
    bucket_name = o.netloc
    dashboard_log_key = o.path.lstrip("/")

    # Transform dashboard JSON path to eval zip path
    # From: logs/prod/.../filename.eval.dashboard.json
    # To:   logs/prod/.../filename.eval.zip
    zipped_eval_log_key = dashboard_log_key.replace(".dashboard.json", ".zip")

    return bucket_name, zipped_eval_log_key
