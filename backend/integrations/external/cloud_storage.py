"""
Cloud Storage Integration
AWS S3, Google Drive, OneDrive support
"""
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
import httpx
import logging
import os

logger = logging.getLogger(__name__)


class CloudStorageService:
    """Cloud storage service for file management"""

    def __init__(self):
        self.s3_client = None
        self.google_drive_token: Optional[str] = None
        self.onedrive_token: Optional[str] = None

    def initialize_s3(
        self,
        aws_access_key: str,
        aws_secret_key: str,
        region: str = "us-east-1"
    ):
        """Initialize AWS S3 client"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        logger.info("S3 client initialized")

    async def upload_to_s3(
        self,
        bucket: str,
        key: str,
        file_content: bytes,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to S3

        Args:
            bucket: S3 bucket name
            key: Object key (file path)
            file_content: File content
            metadata: File metadata

        Returns:
            Upload result
        """
        try:
            if not self.s3_client:
                return {'success': False, 'error': 'S3 client not initialized'}

            # Upload file
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=file_content,
                Metadata=metadata or {}
            )

            # Generate presigned URL (valid for 1 hour)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=3600
            )

            logger.info(f"Uploaded to S3: {bucket}/{key}")
            return {
                'success': True,
                'bucket': bucket,
                'key': key,
                'url': url
            }

        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return {'success': False, 'error': str(e)}

    async def download_from_s3(
        self,
        bucket: str,
        key: str
    ) -> Optional[bytes]:
        """
        Download file from S3

        Args:
            bucket: S3 bucket name
            key: Object key

        Returns:
            File content
        """
        try:
            if not self.s3_client:
                return None

            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read()

            logger.info(f"Downloaded from S3: {bucket}/{key}")
            return content

        except ClientError as e:
            logger.error(f"S3 download error: {e}")
            return None

    async def delete_from_s3(
        self,
        bucket: str,
        key: str
    ) -> bool:
        """
        Delete file from S3

        Args:
            bucket: S3 bucket name
            key: Object key

        Returns:
            Success status
        """
        try:
            if not self.s3_client:
                return False

            self.s3_client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"Deleted from S3: {bucket}/{key}")
            return True

        except ClientError as e:
            logger.error(f"S3 delete error: {e}")
            return False

    async def list_s3_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000
    ) -> list:
        """
        List objects in S3 bucket

        Args:
            bucket: S3 bucket name
            prefix: Object prefix filter
            max_keys: Maximum number of objects

        Returns:
            List of objects
        """
        try:
            if not self.s3_client:
                return []

            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })

            return objects

        except ClientError as e:
            logger.error(f"S3 list error: {e}")
            return []

    async def upload_to_google_drive(
        self,
        file_name: str,
        file_content: bytes,
        folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Google Drive

        Args:
            file_name: File name
            file_content: File content
            folder_id: Parent folder ID

        Returns:
            Upload result
        """
        try:
            if not self.google_drive_token:
                return {'success': False, 'error': 'Google Drive not configured'}

            async with httpx.AsyncClient() as client:
                # Upload file
                headers = {
                    'Authorization': f'Bearer {self.google_drive_token}',
                    'Content-Type': 'application/octet-stream'
                }

                params = {'uploadType': 'media', 'name': file_name}
                if folder_id:
                    params['parents'] = [folder_id]

                response = await client.post(
                    'https://www.googleapis.com/upload/drive/v3/files',
                    headers=headers,
                    params=params,
                    content=file_content
                )

                if response.status_code == 200:
                    file_data = response.json()
                    logger.info(f"Uploaded to Google Drive: {file_name}")
                    return {'success': True, 'file': file_data}
                else:
                    return {'success': False, 'error': response.text}

        except Exception as e:
            logger.error(f"Google Drive upload error: {e}")
            return {'success': False, 'error': str(e)}

    async def upload_to_onedrive(
        self,
        file_name: str,
        file_content: bytes,
        folder_path: str = "/"
    ) -> Dict[str, Any]:
        """
        Upload file to OneDrive

        Args:
            file_name: File name
            file_content: File content
            folder_path: Folder path

        Returns:
            Upload result
        """
        try:
            if not self.onedrive_token:
                return {'success': False, 'error': 'OneDrive not configured'}

            async with httpx.AsyncClient() as client:
                # Upload file
                headers = {
                    'Authorization': f'Bearer {self.onedrive_token}',
                    'Content-Type': 'application/octet-stream'
                }

                url = (
                    f'https://graph.microsoft.com/v1.0/me/drive/root:'
                    f'{folder_path}/{file_name}:/content'
                )

                response = await client.put(
                    url,
                    headers=headers,
                    content=file_content
                )

                if response.status_code in [200, 201]:
                    file_data = response.json()
                    logger.info(f"Uploaded to OneDrive: {file_name}")
                    return {'success': True, 'file': file_data}
                else:
                    return {'success': False, 'error': response.text}

        except Exception as e:
            logger.error(f"OneDrive upload error: {e}")
            return {'success': False, 'error': str(e)}

    async def sync_folder(
        self,
        local_path: str,
        cloud_provider: str,
        cloud_path: str
    ) -> Dict[str, Any]:
        """
        Sync local folder with cloud storage

        Args:
            local_path: Local folder path
            cloud_provider: Cloud provider (s3, gdrive, onedrive)
            cloud_path: Cloud folder path

        Returns:
            Sync result
        """
        try:
            uploaded_files = []
            failed_files = []

            # Walk through local directory
            for root, dirs, files in os.walk(local_path):
                for file in files:
                    local_file = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file, local_path)

                    # Read file content
                    with open(local_file, 'rb') as f:
                        content = f.read()

                    # Upload based on provider
                    if cloud_provider == 's3':
                        result = await self.upload_to_s3(
                            bucket=cloud_path,
                            key=relative_path,
                            file_content=content
                        )
                    elif cloud_provider == 'gdrive':
                        result = await self.upload_to_google_drive(
                            file_name=relative_path,
                            file_content=content
                        )
                    elif cloud_provider == 'onedrive':
                        result = await self.upload_to_onedrive(
                            file_name=relative_path,
                            file_content=content,
                            folder_path=cloud_path
                        )
                    else:
                        continue

                    if result.get('success'):
                        uploaded_files.append(relative_path)
                    else:
                        failed_files.append(relative_path)

            logger.info(
                f"Folder sync: {len(uploaded_files)} uploaded, "
                f"{len(failed_files)} failed"
            )

            return {
                'success': True,
                'uploaded': uploaded_files,
                'failed': failed_files
            }

        except Exception as e:
            logger.error(f"Folder sync error: {e}")
            return {'success': False, 'error': str(e)}


# Global cloud storage service instance
cloud_storage = CloudStorageService()
