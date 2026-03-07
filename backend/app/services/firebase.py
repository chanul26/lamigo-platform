import firebase_admin
from firebase_admin import credentials, auth

#Saving the credentials file in the backend/app/credentials folder and initializing the firebase admin sdk with the credentials file
cred = credentials.Certificate("credentials/firebase-credentials.json")
firebase_admin.initialize_app(cred)

# Created the function that verifies the token sent by the frontend and returns the decoded token if the verification is successful, otherwise it raises an error with the message "Token Verification Failed: " followed by the error message from the exception.
def verify_firebase_token(token: str):
    """
    Use try and except
    to catch any exception print message indicate
    that the token verification failed and include the error message from the exception. 
    """
    
    try:
        decode_token = auth.verify_id_token(token)
        return decode_token
    except Exception as e:
        raise ValueError("Token Verification Failed: " + str(e))
    