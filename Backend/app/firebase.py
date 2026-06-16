import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def _ensure_firebase_initialized():
    """Initialize Firebase lazily so the app can be imported without credentials (e.g. in tests).

    In production the service-account JSON is provided via the FIREBASE_CREDENTIALS
    env var (the file itself is gitignored and never deployed). Locally it falls
    back to the firebase_credentials.json file.
    """
    if not firebase_admin._apps:
        raw = os.environ.get("FIREBASE_CREDENTIALS")
        if raw:
            cred = credentials.Certificate(json.loads(raw))
        else:
            cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    _ensure_firebase_initialized()
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
