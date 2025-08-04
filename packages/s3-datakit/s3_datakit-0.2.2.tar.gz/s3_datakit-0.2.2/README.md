# S3 DataKit 🧰

A Python toolkit to simplify common operations between Amazon S3 and Pandas DataFrames.

## Key Features

* **List** files in an S3 bucket.
* **Upload** local files to S3.
* **Download** files from S3 directly to a local path or a Pandas DataFrame.
* Supports **CSV** and **Stata (.dta)** when reading into DataFrames.

## Installation

```bash
pip install s3-datakit
```

## Credential Configuration

This package uses `boto3` to interact with AWS. `boto3` will automatically search for credentials in the following order:

1.  Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.).
2.  The AWS CLI credentials file (`~/.aws/credentials`).
3.  IAM roles (if running on an EC2 instance or ECS container).

For local development, the easiest method is to use a `.env` file.

**1. Install `python-dotenv` in your project (not as a library dependency):**
```bash
pip install python-dotenv
```

**2. Create a `.env` file in your project's root:**
```
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
AWS_DEFAULT_REGION=your-region # e.g., us-east-1
```

**3. Load the variables in your script *before* using `s3datakit`:**
```python
from dotenv import load_dotenv
import s3datakit as s3dk

# Load environment variables from .env
load_dotenv()

# Now you can use the package's functions
s3dk.list_s3_files(bucket="my-bucket")
```

## Usage

### List Files

```python
import s3datakit as s3dk

file_list = s3dk.list_s3_files(bucket="my-data-bucket")
if file_list:
    print(file_list)
```

### Upload a File

```python
import s3datakit as s3dk

s3dk.upload_s3_file(
    local_path="reports/report.csv",
    bucket="my-data-bucket",
    s3_path="final-reports/report_2025.csv"
)
```

### Download a File

**Option 1: Download to a local path**
```python
import s3datakit as s3dk

local_file = s3dk.download_s3_file(
    bucket="my-data-bucket",
    s3_path="final-reports/report_2025.csv",
    local_path="downloads/report.csv"
)
print(f"File downloaded to: {local_file}")
```

**Option 2: Download directly to a Pandas DataFrame**
```python
import s3datakit as s3dk

df = s3dk.download_s3_file(
    bucket="my-data-bucket",
    s3_path="stata-data/survey.dta",
    to_df=True
)
print(df.head())
```