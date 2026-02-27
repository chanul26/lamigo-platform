"""
LamiGo Security Module
Handles JWT token creation/verification and password hashing

TODO: Implement when authentication is needed
- Currently using Firebase Auth for authentication
- This module is prepared for future JWT-based auth if needed
"""

from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
        
    TODO: Implement with python-jose when needed
    """
    raise NotImplementedError("JWT token creation not yet implemented - using Firebase Auth")


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        Decoded payload if valid, None otherwise
        
    TODO: Implement with python-jose when needed
    """
    raise NotImplementedError("JWT token verification not yet implemented - using Firebase Auth")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
        
    TODO: Implement with passlib when needed
    """
    raise NotImplementedError("Password hashing not yet implemented - using Firebase Auth")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
        
    TODO: Implement with passlib when needed
    """
    raise NotImplementedError("Password verification not yet implemented - using Firebase Auth")
