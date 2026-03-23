import uuid
from datetime import datetime, timezone
import logging
from app.core.dynamodb import dynamodb_resource

logger = logging.getLogger(__name__)

# This matches the table name from your LamiGo architecture PDF
AUDIT_TABLE_NAME = "LamiGo_SystemAuditLogs"

def log_audit_action(actor_id: str, action: str, resource_id: str, resource_type: str, details: dict = None):
    """
    Writes a structured audit log to DynamoDB.
    """
    try:
        table = dynamodb_resource.Table(AUDIT_TABLE_NAME)
        
        # Build the item exactly as DynamoDB expects it
        item = {
            "log_id": str(uuid.uuid4()),                  # Partition Key
            "actor_id": actor_id,                         # Who did it?
            "action": action,                             # e.g., "UPDATE", "CREATE"
            "resource_id": str(resource_id),              # ID of the thing affected
            "resource_type": resource_type,               # e.g., "Recipient", "Branch"
            "details": details or {},                     # Extra JSON data
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into AWS
        table.put_item(Item=item)
        logger.info(f"Successfully logged audit action: {action} on {resource_type}")
        
    except Exception as e:
        # We don't want a logging failure to crash the main app, so we just log the error
        logger.error(f"Failed to write to DynamoDB Audit Log: {e}")