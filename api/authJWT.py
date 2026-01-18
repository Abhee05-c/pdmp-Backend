from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone


Secret_key="b304029d3868991d14359295e963df3b557110af6258663d90a8fa640db79f27"
ALGORITHM="HS256"
Access_Token_Expire_Minutes=30

argon2_context=CryptContext(schemes=["argon2"],deprecated="auto")

def hash_password(password:str) -> str :
    return argon2_context.hash(password)

def verify_hash(password:str,hash:str) -> bool:
    return argon2_context.verify(password,hash)

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=Access_Token_Expire_Minutes)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,Secret_key,algorithm=ALGORITHM)