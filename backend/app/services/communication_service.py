import uuid
import logging
from datetime import datetime, timezone, timedelta
from app.core.dynamodb import dynamodb_resource

logger = logging.getLogger(__name__)

SMS_TABLE_NAME = "LamiGo_SMSLogs"

def log_sms(package_id: str, recipient_phone: str, message_body: str, category: str, status: str):
    """
    Asynchronously logs an SMS message to DynamoDB with a 90-day auto-delete (TTL).
    """
    try:
        table = dynamodb_resource.Table(SMS_TABLE_NAME)
        
        # Calculate the exact second this message should self-destruct (90 days from now)
        expiration_time = int((datetime.now(timezone.utc) + timedelta(days=90)).timestamp())
        
        item = {
            "sms_id": str(uuid.uuid4()),                          # Main Partition Key
            "package_id": str(package_id),                        # GSI 1 Partition Key
            "recipient_phone": recipient_phone,                   # GSI 2 Partition Key
            "message_body": message_body,
            "category": category,                                 # e.g., "DELIVERY_UPDATE"
            "status": status,                                     # e.g., "SENT"
            "created_at": datetime.now(timezone.utc).isoformat(), # Sort Key for both GSIs
            "ttl": expiration_time                                # The AWS auto-delete trigger
        }
        
        table.put_item(Item=item)
        
    except Exception as e:
        # We only log the error so a failed text log doesn't crash the main delivery flow
        logger.error(f"Failed to log SMS to DynamoDB: {e}")