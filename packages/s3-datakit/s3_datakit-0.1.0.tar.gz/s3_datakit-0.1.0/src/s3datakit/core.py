import os
from pathlib import Path
import pandas as pd
import boto3
from botocore.exceptions import ClientError

# NOTE: load_dotenv() is removed from the library.
# The end-user is responsible for managing their credentials.

def _read_file_to_df(file_path: str) -> pd.DataFrame:
    """Helper function to read a file into a Pandas DataFrame."""
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    if file_path.endswith(".dta"):
        return pd.read_stata(file_path)
    # Raise an error if the file format is not supported
    raise ValueError(f"Unsupported file format for: {file_path}")

def list_s3_files(bucket: str) -> list[str]:
    """
    Lists all object keys (files) in an S3 bucket.

    :param bucket: The name of the S3 bucket.
    :return: A list of file names (keys).
    :raises ClientError: If the bucket does not exist or permissions are denied.
    """
    s3 = boto3.client('s3')
    file_list = []
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket)
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                file_list.append(obj['Key'])
    return file_list

def upload_s3_file(local_path: str, bucket: str, s3_path: str | None = None) -> bool:
    """
    Uploads a file to an S3 bucket.

    :param local_path: The path to the local file to upload.
    :param bucket: The destination S3 bucket.
    :param s3_path: The destination path (key) in S3. If None, the local filename is used.
    :return: True if the upload was successful, False otherwise.
    """
    if s3_path is None:
        s3_path = os.path.basename(local_path)
    
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(local_path, bucket, s3_path)
    except (ClientError, FileNotFoundError) as e:
        print(f"❌ Error uploading file: {e}")
        return False
    return True

def download_s3_file(
        bucket: str,
        s3_path: str,
        local_path: str,
        to_df: bool = False
) -> pd.DataFrame | str:
    """
    Downloads a file from S3 to a local path, with an option to load it into a DataFrame.

    :param bucket: The name of the S3 bucket.
    :param s3_path: The path (key) of the file within the bucket.
    :param local_path: The local path where the file will be saved.
    :param to_df: If True, returns a Pandas DataFrame. If False, returns the local file path.
    :return: A Pandas DataFrame or the path to the local file.
    :raises ClientError: If there is a permissions issue or the file/bucket does not exist.
    :raises ValueError: If to_df is True and the file format is not supported.
    """
    path_obj = Path(local_path)
    
    # Download only if the file does not already exist locally
    if not path_obj.is_file():
        # Ensure the destination directory exists
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        s3 = boto3.client('s3')
        s3.download_file(bucket, s3_path, str(path_obj))

    if to_df:
        return _read_file_to_df(str(path_obj))
    
    return str(path_obj)