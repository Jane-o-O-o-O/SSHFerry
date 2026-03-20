from __future__ import annotations
from pydantic import BaseModel, Field

class AuthLoginRequest(BaseModel):
    username:str=Field(min_length=1)
    password:str=Field(min_length=1)

class AuthSignupRequest(BaseModel):
    username:str=Field(min_length=1)
    password:str=Field(min_length=8)
    display_name:str|None=Field(default=None, max_length=64)

class AuthUserResponse(BaseModel):
    id:str
    username:str
    display_name:str
    role:str
    auth_scheme:str
    session_id:str
    session_expires_at:int

class AuthLegacySessionResponse(BaseModel):
    token:str
    header_name:str
    token_type:str
