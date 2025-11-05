from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
bearer_scheme = HTTPBearer()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(user_id: int):
    payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(hours=2)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = decode_token(token)
        return int(payload["user_id"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
