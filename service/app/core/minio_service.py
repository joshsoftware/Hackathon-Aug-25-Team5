from minio import Minio
from minio.error import S3Error
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class MinIOService:
    def __init__(self):
        # Get MinIO settings with fallbacks
        endpoint = settings.MINIO_ENDPOINT or "minio:9000"
        access_key = settings.MINIO_ACCESS_KEY or "admin"
        secret_key = settings.MINIO_SECRET_KEY or "password123"
        secure = settings.MINIO_SECURE
        
        # Parse the endpoint to remove protocol
        endpoint = endpoint.replace("http://", "").replace("https://", "")
        
        logger.info(f"Initializing MinIO client with endpoint: {endpoint}")
        
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        logger.info("MinIO client initialized successfully")
    
    def initialize_buckets(self):
        """Initialize required buckets for the application"""
        buckets = ["documents", "images", "exports"]
        
        for bucket_name in buckets:
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    logger.info(f"Created bucket: {bucket_name}")
                else:
                    logger.info(f"Bucket already exists: {bucket_name}")
            except S3Error as e:
                logger.error(f"Error creating bucket {bucket_name}: {e}")
    
    def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        """Upload a file to MinIO"""
        try:
            self.client.fput_object(bucket_name, object_name, file_path)
            logger.info(f"Uploaded {file_path} to {bucket_name}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            return False
    
    def download_file(self, bucket_name: str, object_name: str, file_path: str):
        """Download a file from MinIO"""
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
            logger.info(f"Downloaded {bucket_name}/{object_name} to {file_path}")
            return True
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            return False
    
    def list_objects(self, bucket_name: str, prefix: str = ""):
        """List objects in a bucket"""
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing objects: {e}")
            return []

# Global instance
minio_service = MinIOService()