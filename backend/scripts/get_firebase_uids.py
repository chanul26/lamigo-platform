import firebase_admin
from firebase_admin import auth, credentials
import os
import sys

# 1. Setup the path to your credentials
# Make sure this matches the path in your .env file
CERT_PATH = "backend/credentials/firebase-adminsdk.json"

if not os.path.exists(CERT_PATH):
    print(f"❌ Error: Credentials file not found at {CERT_PATH}")
    sys.exit(1)

# 2. Initialize Firebase Admin SDK
cred = credentials.Certificate(CERT_PATH)
firebase_admin.initialize_app(cred)

# 3. List of your LamiGo test numbers
phone_numbers = [
    "+94713230532",  # Manager 1
    "+94774384919",  # Manager 2
    "+94703595518",  # Driver 1
    "+94774779060",  # Driver 2
    "+94761997415",  # Driver 3
    "+94723117233"   # Driver 4 (Optional)
]

print("\n" + "="*60)
print("🛡️  LAMIGO FIREBASE USER PRE-REGISTRATION")
print("="*60)

for phone in phone_numbers:
    try:
        # Check if user already exists
        try:
            user = auth.get_user_by_phone_number(phone)
            status = "FOUND"
        except auth.UserNotFoundError:
            # Create user if they don't exist
            user = auth.create_user(phone_number=phone)
            status = "CREATED"
        
        print(f"✅ [{status}] {phone}  -->  UID: {user.uid}")
        
    except Exception as e:
        print(f"❌ Error for {phone}: {e}")

print("="*60)
print("👉 Copy these UIDs and paste them into seed_dummy_data.py\n")