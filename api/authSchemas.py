from pydantic import BaseModel,EmailStr

class SignupRequest(BaseModel):
    org_name:str
    org_email:str
    username:str
    password:str

class LoginRequest(BaseModel):
    username:str
    password:str

class CreateOrgUserRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token:str
    token_type:str="bearer"
    