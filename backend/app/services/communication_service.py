from boto3.dynamodb.conditions import Key
import requests
import uuid
import logging
from datetime import datetime, timezone, timedelta
from app.core.dynamodb import dynamodb_resource
from app.core.config import settings

logger = logging.getLogger(__name__)

SMS_TABLE_NAME = "LamiGo_SMSLogs"

def log_sms(package_id: str, recipient_phone: str, message_body: str, category: str, status: str):
    """
    Sends an SMS via Notify.lk and then asynchronously logs it to DynamoDB.
    """
    # 1. SEND THE REAL SMS VIA NOTIFY.LK
    try:
        if settings.NOTIFY_USER_ID and settings.NOTIFY_API_KEY:
            # Bulletproof Phone Number Formatting for Notify.lk
            formatted_phone = recipient_phone.strip().replace("+", "").replace(" ", "")
            if formatted_phone.startswith("07"):
                formatted_phone = "94" + formatted_phone[1:]
            
            payload = {
                "user_id": settings.NOTIFY_USER_ID,
                "api_key": settings.NOTIFY_API_KEY,
                "sender_id": settings.NOTIFY_SENDER_ID or "NotifyDEMO",
                "to": formatted_phone,
                "message": message_body
            }
            
            response = requests.post("https://app.notify.lk/api/v1/send", data=payload, timeout=5)
            
            if response.status_code == 200:
                status = "SENT" 
            else:
                # THIS WILL PRINT THE EXACT REASON IT FAILED IN YOUR DOCKER LOGS
                logger.error(f"Notify.lk API Error: {response.text}")
                print(f"🚨 SMS FAILED: {response.text}") 
                status = "FAILED"
        else:
            print("🚨 SMS SKIPPED: Notify.lk API keys are missing inside the Docker container!")
    except Exception as e:
        logger.error(f"Failed to send SMS via Notify.lk: {e}")
        print(f"🚨 SMS CRASH: {e}")
        status = "FAILED"
        
    # 2. LOG TO DYNAMODB
    try:
        table = dynamodb_resource.Table(SMS_TABLE_NAME)
        expiration_time = int((datetime.now(timezone.utc) + timedelta(days=90)).timestamp())
        
        item = {
            "sms_id": str(uuid.uuid4()),                          
            "package_id": str(package_id),                        
            "recipient_phone": recipient_phone,                   
            "message_body": message_body,
            "category": category,                                 
            "status": status,                                     
            "created_at": datetime.now(timezone.utc).isoformat(), 
            "ttl": expiration_time                                
        }
        table.put_item(Item=item)
        
    except Exception as e:
        logger.error(f"Failed to log SMS to DynamoDB: {e}")

def log_call(user_id: str, recipient_phone: str, task_id: str, role: str, duration_seconds: int = 0):
    """
    Asynchronously logs a phone call to DynamoDB with a 180-day auto-delete (TTL).
    """
    try:
        table = dynamodb_resource.Table("LamiGo_CallLogs")
        
        # Calculate the exact second this record should self-destruct (180 days from now)
        expiration_time = int((datetime.now(timezone.utc) + timedelta(days=180)).timestamp())
        
        item = {
            "call_id": str(uuid.uuid4()),                         # Main Partition Key
            "user_id": str(user_id),                              # GSI 1 Partition Key
            "task_id": str(task_id),                              # GSI 2 Partition Key
            "recipient_phone": recipient_phone,                   # GSI 3 Partition Key
            "role": role,                                         # e.g., "DRIVER" or "STATION_MANAGER"
            "duration_seconds": duration_seconds,
            "created_at": datetime.now(timezone.utc).isoformat(), # Sort Key for all 3 GSIs
            "ttl": expiration_time                                # The AWS auto-delete trigger
        }
        
        table.put_item(Item=item)
        
    except Exception as e:
        logger.error(f"Failed to log Call to DynamoDB: {e}")

def get_sms_history_by_package(package_id: str) -> list:
    """
    Fetches all SMS logs for a specific package, newest first.
    Uses the GSI_PackageHistory index.
    """
    try:
        table = dynamodb_resource.Table("LamiGo_SMSLogs")
        response = table.query(
            IndexName='GSI_PackageHistory',
            KeyConditionExpression=Key('package_id').eq(str(package_id)),
            ScanIndexForward=False  # False means return the newest messages first
        )
        return response.get('Items', [])
    except Exception as e:
        logger.error(f"Failed to fetch SMS history for package {package_id}: {e}")
        return []

def get_call_history_by_user(user_id: str) -> list:
    """
    Fetches all Call logs made by a specific employee, newest first.
    Uses the GSI_UserCallHistory index.
    """
    try:
        table = dynamodb_resource.Table("LamiGo_CallLogs")
        response = table.query(
            IndexName='GSI_UserCallHistory',
            KeyConditionExpression=Key('user_id').eq(str(user_id)),
            ScanIndexForward=False
        )
        return response.get('Items', [])
    except Exception as e:
        logger.error(f"Failed to fetch Call history for user {user_id}: {e}")
        return []