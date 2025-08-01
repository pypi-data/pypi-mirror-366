from os import getenv
import aioboto3
import logging

class S3Client:

    def __init__(self, s3_region_override:str=None):
        self.session = aioboto3.Session()
        
        self.region_name = getenv('AWS_S3_REGION') if s3_region_override is None else s3_region_override

        assert self.region_name, "AWS_S3_REGION environment variable must be set, or the region override s3 client parameter must be used."

    async def upload_file(self, local_file_path: str, bucket_name: str, s3_key: str) -> bool:
        """Asynchronously uploads a file to an S3 bucket.
        Example:
            await client.upload_file('local_file.txt', 'my-bucket', 'folder/remote_file.txt')
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.upload_file(local_file_path, bucket_name, s3_key)
            return True
        except Exception as e:
            logging.error(f"Upload failed: {e}")
            return False

    async def download_file(self, bucket_name: str, s3_key: str, local_file_path: str) -> bool:
        """Asynchronously downloads a file from an S3 bucket.
        Example:
            await client.download_file('my-bucket', 'folder/remote_file.txt', 'downloaded_file.txt')
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.download_file(bucket_name, s3_key, local_file_path)
            return True
        except Exception as e:
            logging.error(f"Download failed: {e}")
            return False

    async def upload_json(self, bucket_name: str, object_key: str, json_str: str) -> bool:
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.put_object(
                    Bucket=bucket_name,
                    Key=object_key,
                    Body=json_str,
                    ContentType='application/json'
                )
            return True
        except Exception as e:
            logging.error(f"Upload JSON failed: {e}")
            return False

async_s3_client = S3Client()  # module level singleton instance
