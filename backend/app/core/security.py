from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
import logging

logger = logging.getLogger(__name__)

# MAGIC: This is the FastAPI tool that creates the "Authorize" padlock in Swagger UI.
# It automatically looks for "Authorization: Bearer <token>" in the HTTP headers.
token_auth_scheme = HTTPBearer()

def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> dict:
    """
    Extracts the Bearer token from the header (sent by Flutter, NextJS, or Swagger UI)
    and verifies its cryptographic signature with Google Firebase.
    Returns the decoded token payload (which contains the 'uid').
    """
    # Extract the raw string token from the credentials object
    raw_token = credentials.credentials
    
    try:
        # Ask Google's servers if this token is real and hasn't expired
        decoded_token = auth.verify_id_token(raw_token)
        return decoded_token
        
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token. Are you sure this is a Firebase token?",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected Firebase auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )