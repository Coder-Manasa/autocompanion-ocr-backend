# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import firebase_admin
from firebase_admin import credentials, auth

from app.core.config import settings

# Initialise Firebase Admin exactly once
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_FILE)
    firebase_admin.initialize_app(cred)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Extract Bearer token from Authorization header and verify with Firebase.
    Returns the decoded token (dict) on success.
    """
    token = credentials.credentials

    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token",
        )
