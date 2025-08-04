import os
from pathlib import Path
import pandas as pd
import boto3
from botocore.exceptions import ClientError

# NOTE: load_dotenv() is removed from the library.
# The end-user is responsible for managing their credentials.


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

def _read_file_to_df(file_path: str) -> pd.DataFrame:
    """Helper function to read a file into a Pandas DataFrame."""
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    if file_path.endswith(".dta"):
        # Requires the 'pyreadstat' package
        return pd.read_stata(file_path)
    raise ValueError(f"Unsupported file format for DataFrame: {file_path}")

def download_s3_file(
        bucket: str,
        s3_path: str,
        local_path: str | None = None,
        to_df: bool = False
) -> pd.DataFrame | str:
    """
    Downloads a file from S3, defaulting to a 'data/' subdirectory.

    :param bucket: The name of the S3 bucket.
    :param s3_path: The path (key) of the file within the bucket.
    :param local_path: Optional. The local path to save the file.
                       If not provided, defaults to 'data/[original_filename]'.
    :param to_df: If True, returns a Pandas DataFrame.
    :return: A Pandas DataFrame or the path to the local file.
    """
    # If no local_path is given, create a default one.
    if local_path is None:
        filename = os.path.basename(s3_path)
        local_path = f"data/{filename}"

    path_obj = Path(local_path)

    if path_obj.is_file():
        print(f"ℹ️ File already exists at '{local_path}'. Skipping download.")
    else:
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        s3 = boto3.client('s3')
        try:
            meta_data = s3.head_object(Bucket=bucket, Key=s3_path)
            total_size = int(meta_data.get('ContentLength', 0))
            progress_callback = ProgressPercentage(s3_path, total_size)
            
            print(f"⬇️ Preparing to download '{s3_path}' ({total_size / 1e6:.2f} MB)")
            s3.download_file(bucket, s3_path, str(path_obj), Callback=progress_callback)
            
            sys.stdout.write("\n")
            print("✅ Download complete.")
        except ClientError as e:
            sys.stdout.write("\n")
            print(f"❌ Error during download: {e}")
            raise

    if to_df:
        return _read_file_to_df(str(path_obj))

    return str(path_obj)