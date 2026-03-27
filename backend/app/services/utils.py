import random
import string
from uuid import UUID

def generate_package_tracking_id(branch_id: UUID) -> str:
    """
    Generates a unique-ish human-readable tracking ID for packages.
    Format: LMG-[5-CHAR-BRANCH-SLICE]-[5-CHAR-RANDOM-SUFFIX]
    Example: LMG-F47AC-9A2B7
    """
    # 1. Take a 5-character slice of the Branch UUID
    prefix = str(branch_id)[:5].upper()
    
    # 2. Generate a random 5-character alphanumeric suffix
    # We use string.ascii_uppercase and string.digits (A-Z, 0-9)
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    
    return f"LMG-{prefix}-{suffix}"