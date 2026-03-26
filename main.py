#
# File: main.py
# Author: Daniel Oliveira
#

### FastAPI app connecting user interface and the chatbot ###

from __future__ import annotations

import os
import re
import bcrypt
from datetime import datetime, timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from chatbot import communicate
from db import create_user, get_balance, get_user
from models import LoginRequest, PredictRequest, PredictResponse, RegisterRequest, UserContext

load_dotenv()

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ.get('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 60))

# Initialize FastAPI app #

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


## JWT helpers ##

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload['exp'] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


## Auth dependencies ##

def get_current_user_api(request: Request) -> UserContext:
    """For API routes: return 401 JSON on auth failure."""
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=401, detail='Not authenticated')
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail='Invalid token')
    return UserContext(
        id=payload['id'],
        username=payload['username'],
        name=payload['name'],
        balance=payload['balance'],
    )


## Login ##

@app.post('/crexusers/', name='login')
def login(body: LoginRequest):
    account = get_user(body.username)
    if not account or not bcrypt.checkpw(body.password.encode('utf-8'), account['password'].encode('utf-8')):
        raise HTTPException(status_code=401, detail='Incorrect username/password!')
    token = create_access_token({
        'id': account['id'],
        'username': account['username'],
        'name': account['name'],
        'balance': account['balance'],
    })
    response = JSONResponse(content={
        'username': account['username'],
        'name': account['name'],
        'balance': account['balance'],
    })
    response.set_cookie(key='access_token', value=token, httponly=True, samesite='lax', max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return response


## Logout ##

@app.post('/crexusers/logout', name='logout')
def logout():
    response = JSONResponse(content={'message': 'Logged out'})
    response.delete_cookie('access_token')
    return response


## Register ##

@app.post('/crexusers/register', name='register')
def register(body: RegisterRequest):
    if get_user(body.username):
        raise HTTPException(status_code=400, detail='Account already exists!')
    if not re.match(r'[^@]+@[^@]+\.[^@]+', body.email):
        raise HTTPException(status_code=400, detail='Invalid email address!')
    if not re.match(r'[A-Za-z0-9]+', body.username):
        raise HTTPException(status_code=400, detail='Username must contain only characters and numbers!')
    password_hash = bcrypt.hashpw(body.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    create_user(body.username, body.name, password_hash, body.email)
    return JSONResponse(content={'message': 'You have successfully registered!'}, status_code=201)


## Home ##

@app.get('/crexusers/home', name='home')
def home(current_user: Annotated[UserContext, Depends(get_current_user_api)]):
    balance = get_balance(current_user.id)
    return JSONResponse(content={
        'name': current_user.name,
        'username': current_user.username,
        'balance': balance,
    })


## Predict ##

@app.post('/crexusers/predict', name='predict', response_model=PredictResponse)
def predict(
    body: PredictRequest,
    current_user: Annotated[UserContext, Depends(get_current_user_api)],
):
    answer = communicate(body.message, id=current_user.id, name=current_user.name)
    return PredictResponse(answer=answer)
