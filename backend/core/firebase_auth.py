import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.settings import settings
import os
import json

# Initialize Firebase app only once
if not firebase_admin._apps:
    cred_json = settings.FIREBASE_JSON
    if cred_json:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        print("non cred")
        firebase_admin.initialize_app()

bearer_scheme = HTTPBearer()

def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or missing Firebase ID token.") 