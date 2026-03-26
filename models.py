#
# File: models.py
# Author: Daniel Oliveira
#

### Pydantic v2 request/response models ###

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UserContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    name: str
    balance: int


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    name: str
    password: str
    email: str


class PredictRequest(BaseModel):
    message: str


class PredictResponse(BaseModel):
    answer: str
