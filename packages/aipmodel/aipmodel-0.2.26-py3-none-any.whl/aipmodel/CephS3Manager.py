import os
import sys
import boto3
from tqdm import tqdm
from botocore.exceptions import ClientError, EndpointConnectionError

# CephS3Manager handles interaction with Ceph-compatible S3 storage
class CephS3Manager:
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket_name = bucket_name

    def ensure_bucket_exists(self):
        try:
            buckets = self.s3.list_buckets()
            names = [b['Name'] for b in buckets.get('Buckets', [])]
            if self.bucket_name not in names:
                try:
                    self.s3.create_bucket(Bucket=self.bucket_name)
                    print(f"[OK] Ceph S3 Bucket Created: {self.bucket_name}")
                except ClientError as e:
                    if e.response['Error']['Code'] == "TooManyBuckets":
                        print(f"[WARN] Bucket limit reached. Please ensure bucket '{self.bucket_name}' exists.")
                    else:
                        raise e
            else:
                print(f"[OK] Ceph S3 Bucket Exists: {self.bucket_name}")
        except Exception as e:
            print(f"[FAIL] Ensure Bucket Error: {e}")

    def check_connection(self):
        try:
            self.s3.list_buckets()
            print("[OK] Ceph S3 Connection")
            return True
        except EndpointConnectionError:
            print("[FAIL] Ceph S3 Connection")
            return False
        except ClientError as e:
            print(f"[FAIL] Ceph S3 ClientError: {e.response['Error']['Code']}")
            return False
        except Exception:
            print("[FAIL] Ceph S3 Unknown")
            return False

    def check_auth(self):
        try:
            self.s3.list_buckets()
            print("[OK] Ceph S3 Auth")
            return True
        except ClientError as e:
            code = e.response['Error']['Code']
            if code in ["InvalidAccessKeyId", "SignatureDoesNotMatch"]:
                print("[FAIL] Ceph S3 Auth Invalid")
            else:
                print(f"[FAIL] Ceph S3 Auth: {code}")
            return False
        except Exception:
            print("[FAIL] Ceph S3 Auth Unknown")
            return False

    def check_if_exists(self, key):
        resp = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=key)
        return resp.get("Contents", []) if "Contents" in resp else None
    
    def get_uri_size(self, uri):
        import re

        # Parse the URI to extract bucket name and object key
        pattern = r'^s3://([^/]+)/(.+)$'
        match = re.match(pattern, uri)
        if not match:
            raise ValueError(f"Invalid S3 URI: {uri}")
        
        bucket, key = match.groups()

        # Ensure the bucket in the URI matches the initialized bucket
        if bucket != self.bucket_name:
            raise ValueError(f"URI bucket '{bucket}' does not match initialized bucket '{self.bucket_name}'")

        try:
            # Try to fetch metadata assuming the key is a file
            response = self.s3.head_object(Bucket=self.bucket_name, Key=key)
            size = response['ContentLength'] / (1024 ** 2)
            print(f"[OK] Found file: {key} ({size:.2f} MB)")
            return size
        except self.s3.exceptions.ClientError as e:
            # If the object does not exist, it might be a folder
            if e.response['Error']['Code'] == '404':
                if not key.endswith("/"):
                    key += "/"
            else:
                raise e

        # Treat the key as a folder prefix and calculate total size of its contents
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=key)

        total_size = 0
        found = False
        for page in tqdm(pages, desc=f"Scanning {uri}"):
            contents = page.get('Contents', [])
            if contents:
                found = True
                for obj in contents:
                    total_size += obj['Size']

        if not found:
            print(f"[WARN] No objects found at URI '{uri}'.")
            return 0.0

        size_mb = total_size / (1024 ** 2)
        print(f"[OK] Folder total size: {size_mb:.2f} MB")
        return size_mb

    
    def is_folder(self, key):
        contents = self.check_if_exists(key)
        return bool(contents) and any(obj['Key'] != key for obj in contents)

    def _download_file_with_progress_bar(self, remote_path, local_path):
        try:
            meta_data = self.s3.head_object(Bucket=self.bucket_name, Key=remote_path)
            total_length = int(meta_data.get('ContentLength', 0))
        except Exception as e:
            print(f"[ERROR] Failed to fetch metadata for '{remote_path}': {e}")
            total_length = None

        with tqdm(
            total=total_length,
            desc=os.path.basename(remote_path),
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            leave=False,
            dynamic_ncols=True,
            ncols=100,
            file=sys.stdout,
            ascii=True
        ) as pbar:
            with open(local_path, 'wb') as f:
                self.s3.download_fileobj(self.bucket_name, remote_path, f, Callback=pbar.update)

    def download_file(self, remote_path, local_path):
        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        try:
            self._download_file_with_progress_bar(remote_path, local_path)
            print(f"Downloaded '{remote_path}' to '{local_path}'")
        except Exception as e:
            print(f"Error downloading file '{remote_path}': {e}")

    def download_folder(self, remote_folder, local_folder, keep_folder=False, exclude=[], overwrite=False):
        if not remote_folder.endswith("/"):
            remote_folder += "/"
        resp = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=remote_folder)
        if "Contents" not in resp:
            print(f"[FAIL] Folder {remote_folder} not found")
            return
        print(f"Downloading folder '{remote_folder}' to '{local_folder}'...")
        if keep_folder:
            local_folder = os.path.join(local_folder, remote_folder.split('/')[-2])
        os.makedirs(local_folder, exist_ok=True)
        with tqdm(total=len(resp["Contents"]), desc="Downloading") as pbar:
            for obj in resp["Contents"]:
                file_key = obj["Key"]
                relative_path = file_key[len(remote_folder):]
                if any(x in relative_path for x in exclude):
                    print(f"Skipped file {file_key}. File matches excluded pattern.")
                    continue
                local_file_path = os.path.join(local_folder, relative_path)
                if not overwrite and os.path.exists(local_file_path):
                    print(f"Skipped file {file_key}. File already exists.")
                else:
                    self.download_file(file_key, local_file_path)
                pbar.update(1)

    def download(self, remote_path, local_path, keep_folder=False, exclude=[], overwrite=False):
        if os.path.isfile(local_path) and self.is_folder(remote_path):
            raise ValueError("Cannot download folder to file path")
        if os.path.isdir(local_path) and not self.is_folder(remote_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        if self.is_folder(remote_path):
            self.download_folder(remote_path, local_path, keep_folder=keep_folder, exclude=exclude, overwrite=overwrite)
        else:
            self.download_file(remote_path, local_path)

    def upload_file(self, local_file_path, remote_path):
        self.s3.upload_file(local_file_path, self.bucket_name, remote_path)
        print(f"[Upload] {local_file_path} -> s3://{self.bucket_name}/{remote_path}")

    def upload(self, local_path, remote_path):
        if os.path.isfile(local_path) and self.is_folder(remote_path):
            raise ValueError("Cannot upload file to folder path")
        if os.path.isdir(local_path):
            if self.check_if_exists(remote_path) and not self.is_folder(remote_path):
                raise ValueError("Cannot upload folder to file path")
        if os.path.isdir(local_path):
            for root, _, files in os.walk(local_path):
                for file in files:
                    local_file = os.path.join(root, file)
                    s3_key = os.path.join(remote_path, os.path.relpath(local_file, local_path)).replace("\\", "/")
                    self.upload_file(local_file, s3_key)
        else:
            self.upload_file(local_path, remote_path)

    def delete_folder(self, prefix):
        objects = self.check_if_exists(prefix)
        if objects:
            for obj in objects:
                self.s3.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
            print(f"[Delete] s3://{self.bucket_name}/{prefix}")
