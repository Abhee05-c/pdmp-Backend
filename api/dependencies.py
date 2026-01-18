from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from api.authJWT import Secret_key, ALGORITHM

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def current_user(token: str = Depends(oauth_scheme)):
    print(oauth_scheme)
    print("Using Secret_key:", Secret_key)
    print("Decoding token:", token)
    try:
        payload = jwt.decode(
            token,
            Secret_key,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")
        role = payload.get("role")
        org_id = payload.get("org_id")

        if user_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT token"
        )
