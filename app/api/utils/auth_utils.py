from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from fastapi import Depends, HTTPException
import requests
from jose.exceptions import JWTError
from streamlit import status
from app.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, GOOGLE_CERTS_URL


class AuthUtils:
    # Initialize security settings
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = int(ACCESS_TOKEN_EXPIRE_MINUTES)
        self.google_certs_url = GOOGLE_CERTS_URL
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

    # Password hash utilities
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    # Function to create a JWT token
    def create_access_token(self, data: dict, expires_delta: int = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    # Function to verify a JWT token
    def verify_access_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    # Function to generate a password reset token
    def generate_reset_token(self, user_id: int):
        expiration = datetime.utcnow() + timedelta(minutes=10)
        payload = {"user_id": user_id, "exp": expiration}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    # Function to decode a password reset token
    def decode_reset_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token has expired.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token.")

    # Function to check if a token has expired
    def is_token_expired(self, expiration: int):
        if datetime.utcnow().timestamp() > expiration:
            raise HTTPException(status_code=400, detail="Token has expired.")

    # Function to fetch Google's public keys
    def get_google_public_keys(self):
        try:
            response = requests.get(self.google_certs_url)
            response.raise_for_status()
            return response.json().get('keys', [])
        except requests.RequestException as e:
            print(f"Error fetching Google public keys: {e}")
            return []

    # Function to get the appropriate public key for decoding the id_token
    def get_public_key_from_jwk(self, jwk):
        return jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

    # Function to verify the Google ID token
    def verify_google_id_token(self, id_token: str):
        try:
            response = requests.get(self.google_certs_url)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Unable to fetch Google's public keys")

            public_keys = response.json()
            unverified_header = jwt.get_unverified_header(id_token)
            if unverified_header is None:
                raise HTTPException(status_code=400, detail="Unable to extract header from token")
            
            rsa_key = {}
            for key in public_keys:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            
            if rsa_key:
                payload = jwt.decode(
                    id_token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience="754665354965-oosrn97ournnrdbv7njkubnro4li81vv.apps.googleusercontent.com",
                    issuer="https://accounts.google.com"
                )
                return payload
            else:
                raise HTTPException(status_code=400, detail="Unable to find appropriate key for verification")
        except JWTError as e:
            raise HTTPException(status_code=400, detail="Invalid token or failed verification")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error verifying token: " + str(e))

    # Dependency to get the current user
    def get_current_user(self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
        payload = self.verify_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return payload

