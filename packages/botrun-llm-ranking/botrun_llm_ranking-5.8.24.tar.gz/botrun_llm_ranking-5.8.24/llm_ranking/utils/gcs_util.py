import os
import re
import json
from typing import List, Optional
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account

load_dotenv()


def get_storage_client() -> storage.Client:
    """初始化並返回 GCS client"""
    google_service_account_key_path = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
        "/app/keys/scoop-386004-d22d99a7afd9.json",
    )
    credentials = service_account.Credentials.from_service_account_file(
        google_service_account_key_path,
        scopes=["https://www.googleapis.com/auth/devstorage.read_write"],
    )
    return storage.Client(credentials=credentials)


def create_bucket(bucket_name: str) -> Optional[storage.Bucket]:
    """創建新的 bucket，如果已存在則返回現有的"""
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)

        if not bucket.exists():
            print(f"Creating new bucket: {bucket_name}")
            bucket = storage_client.create_bucket(
                bucket_name, location="asia-east1"  # 指定 bucket 位置為 asia-east1
            )
        else:
            print(f"Bucket {bucket_name} already exists")

        return bucket
    except Exception as e:
        print(f"Error creating bucket {bucket_name}: {str(e)}")
        return None


def list_blobs(bucket_name: str, prefix: str = "") -> List[str]:
    """列出指定 bucket 和前綴（資料夾）下的所有檔案"""
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)

        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    except Exception as e:
        print(f"Error listing blobs in {bucket_name}/{prefix}: {str(e)}")
        return []


def create_blob(bucket_name: str, destination_blob_name: str, content: str) -> bool:
    """在指定的 bucket 中創建新的 blob（檔案）"""
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_string(content)
        print(f"File {destination_blob_name} uploaded to {bucket_name}")
        return True
    except Exception as e:
        print(f"Error creating blob {destination_blob_name}: {str(e)}")
        return False


def delete_blob(bucket_name: str, blob_name: str) -> bool:
    """刪除指定的 blob（檔案）"""
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if blob.exists():
            blob.delete()
            print(f"Blob {blob_name} deleted from {bucket_name}")
            return True
        else:
            print(f"Blob {blob_name} does not exist in {bucket_name}")
            return False
    except Exception as e:
        print(f"Error deleting blob {blob_name}: {str(e)}")
        return False


async def from_gcs(url: str) -> str:
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket("botrun_crawler")

        # 處理 URL 以創建檔案路徑
        clean_url = re.sub(r"^https?://", "", url)
        clean_url = clean_url.replace("/", "_")  # 將斜線替換為底線
        file_path = f"websites/{clean_url}.json"

        print(f"[from_gcs] Looking for file: {file_path}")

        # 檢查檔案是否存在
        blob = bucket.blob(file_path)
        if blob.exists():
            print(f"[from_gcs] Found cached content for: {url}")
            content = blob.download_as_text()
            content_json = json.loads(content)
            return content_json["data"]["html"]

        print(f"[from_gcs] No cached content found for: {url}")
        return None

    except Exception as e:
        print(f"[from_gcs] Error accessing GCS for {url}: {str(e)}")
        return None


def get_blob_content(bucket_name: str, blob_name: str) -> Optional[str]:
    """獲取指定 blob 的內容"""
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if blob.exists():
            return blob.download_as_text()
        else:
            print(f"Blob {blob_name} does not exist in {bucket_name}")
            return None
    except Exception as e:
        print(f"Error getting blob {blob_name}: {str(e)}")
        return None
