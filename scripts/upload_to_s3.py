import boto3
import os
from datetime import datetime, timezone


S3_BUCKET = "opensky-radar-maaz"

LOCAL_FILE = "/opt/airflow/scripts/opensky_raw.csv"


def main():

    if not os.path.exists(LOCAL_FILE):
        raise FileNotFoundError(
            f"Extracted file not found: {LOCAL_FILE}"
        )

    now = datetime.now(timezone.utc)

    s3_key = (
        f"raw/opensky/"
        f"year={now.year}/"
        f"month={now.month:02d}/"
        f"day={now.day:02d}/"
        f"hour={now.hour:02d}/"
        f"opensky_raw.csv"
    )

    print("Uploading file to S3...")
    print(f"Bucket: {S3_BUCKET}")
    print(f"Key: {s3_key}")

    s3 = boto3.client("s3")

    s3.upload_file(
        LOCAL_FILE,
        S3_BUCKET,
        s3_key
    )

    print("\nSuccessfully uploaded to S3:")
    print(f"s3://{S3_BUCKET}/{s3_key}")


if __name__ == "__main__":
    main()
