import boto3
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_dynamodb_resource():
    """
    Initializes and returns a Boto3 DynamoDB Resource object.
    It automatically uses the secure keys validated by our config.py.
    """
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        return dynamodb
    except Exception as e:
        logger.error(f"Failed to connect to AWS DynamoDB: {e}")
        raise e

# Create a single global instance to be used across the app
dynamodb_resource = get_dynamodb_resource()