from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from fastapi import HTTPException
import requests
from jose.exceptions import JWTError as JoseJWTError

# Security settings
SECRET_KEY = "your-secret-key"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes

# Google OAuth Public Key URL
GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

# Password hash utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_reset_token(user_id: int):
    expiration = datetime.utcnow() + timedelta(minutes=10)
    payload = {"user_id": user_id, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Function to create a JWT token
def create_access_token(data: dict, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

# Function to verify a JWT token
def verify_access_token(token: str, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM) -> Optional[dict]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        return None

# Function to fetch Google's public keys
def get_google_public_keys():
    try:
        response = requests.get(GOOGLE_CERTS_URL)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        return response.json().get('keys', [])
    except requests.RequestException as e:
        print(f"Error fetching Google public keys: {e}")
        return []

# Function to get the appropriate public key for decoding the id_token
def get_public_key_from_jwk(jwk):
    return jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

# Function to verify the Google ID token
def verify_google_id_token(id_token: str):
    try:
        # Get Google's public keys to verify the id_token
        response = requests.get(GOOGLE_CERTS_URL)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Unable to fetch Google's public keys")

        public_keys = response.json()

        # Decode the token to get the 'kid' (key ID)
        unverified_header = jwt.get_unverified_header(id_token)
        if unverified_header is None:
            raise HTTPException(status_code=400, detail="Unable to extract header from token")
        
        # Find the correct public key
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
            # Now verify the token using the correct public key
            payload = jwt.decode(
                id_token,
                rsa_key,
                algorithms=["RS256"],  # The algorithm used by Google for ID tokens
                audience="754665354965-oosrn97ournnrdbv7njkubnro4li81vv.apps.googleusercontent.com",
                issuer="https://accounts.google.com"
            )
            return payload  # Return the decoded payload if token is valid
        else:
            raise HTTPException(status_code=400, detail="Unable to find appropriate key for verification")

    except JWTError as e:
        raise HTTPException(status_code=400, detail="Invalid token or failed verification")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error verifying token: " + str(e))
    
def decode_reset_token(token: str):
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token.")

def is_token_expired(expiration: int):
    # Check if the token's expiration timestamp has passed
    if datetime.utcnow().timestamp() > expiration:
        raise HTTPException(status_code=400, detail="Token has expired.")

