# Inside container code
import logging
import os
from typing import Sequence

import boto3
from botocore.client import Config


logger = logging.getLogger(__name__)


# Get MinIO connection details from environment
endpoint = os.environ.get("MINIO_ENDPOINT")
access_key = os.environ.get("MINIO_ACCESS_KEY")
secret_key = os.environ.get("MINIO_SECRET_KEY")

# Connect to MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    config=Config(signature_version="s3v4"),
)


def load_images_directory(dir_path: str, bucket: str, root_folder: str = ""):
    load_directory(
        dir_path=dir_path,
        bucket=bucket,
        extensions=(".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"),
        root_folder=root_folder,
    )


def load_directory(
    dir_path: str,
    bucket: str,
    root_folder: str = "",
    extensions: Sequence[str] = (".*"),
) -> None:
    # Find all images in the directory
    uploaded_count = 0

    # Walk directory tree to find all files
    for root, _, files in os.walk(dir_path):
        for image_file in files:
            # Only process image files
            if image_file.lower().endswith(extensions):
                file_path = os.path.join(root, image_file)

                # Create S3 key that preserves directory structure
                rel_path = os.path.relpath(file_path, dir_path)
                if root_folder:
                    rel_path = os.path.join(root_folder, rel_path)

                # Upload file with preserved path structure
                s3_client.upload_file(file_path, bucket, rel_path)

                uploaded_count += 1
                logger.debug(f"Uploaded {rel_path} to MinIO as {rel_path}")
