from pydantic import BaseModel
from fastapi import UploadFile


class AuthenticationRequest(BaseModel):
    national_id: str
    email: str
    last_name: str
    image1: UploadFile
    image2: UploadFile


class AuthenticationResponse(BaseModel):
    national_id: str
    email: str
    last_name: str
    ip: str
    image1: str
    image2: str
    state: str


class UserStatusRequest(BaseModel):
    national_id: str


class UserStatusResponse(BaseModel):
    state: str
