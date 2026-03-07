from fastapi import Header, HTTPException, Depends
from app.services.firebase import verify_firebase_token

'''
    create the function which get the header from every request,
    and check if the header start with Bearer, if not immediately
    raise an HTTPException with status code 401 and message "Invalid authorization header format",
    if the header is valid, its uses spilit to get the raw token and return it.
'''
def get_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    token = authorization.split(" ")[1]
    return token

'''
    create the function which get the token from the header and verify it using the verify_firebase_token function,
    if the verification is successful, it returns the decoded token, 
    otherwise it raises an HTTPException with status code 401 and
    message "Token Verification Failed: " followed by the error message from the exception.
'''
def get_current_user(token: str = Depends(get_token)):
    try:
        decoded = verify_firebase_token(token)
        return decoded
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))