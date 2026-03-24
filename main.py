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
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt

from chatbot import communicate
from db import create_user, get_balance, get_user
from models import PredictRequest, PredictResponse, UserContext

load_dotenv()

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ.get('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 60))

# Initialize FastAPI app #

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


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

## Exception handler: convert 303 HTTPException to RedirectResponse ##

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 303 and exc.headers and 'Location' in exc.headers:
        return RedirectResponse(url=exc.headers['Location'], status_code=303)
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})

## Auth dependencies ##

def get_current_user(request: Request) -> UserContext:
    """For template routes: redirect to login on auth failure."""
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=303, headers={'Location': '/crexusers/'}, detail='Not authenticated')
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=303, headers={'Location': '/crexusers/'}, detail='Invalid token')
    return UserContext(
        id=payload['id'],
        username=payload['username'],
        name=payload['name'],
        balance=payload['balance'],
    )


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

@app.api_route('/crexusers/', methods=['GET', 'POST'], name='login')
def login(
    request: Request,
    username: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
):
    msg = ''

    if request.method == 'POST':
        if username and password:
            account = get_user(username)
            if account and bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
                token = create_access_token({
                    'id': account['id'],
                    'username': account['username'],
                    'name': account['name'],
                    'balance': account['balance'],
                })
                response = RedirectResponse(url='/crexusers/home', status_code=303)
                response.set_cookie(key='access_token', value=token, httponly=True, samesite='lax', max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
                return response
            else:
                msg = 'Incorrect username/password!'
        else:
            msg = 'Please fill out the form!'

    return templates.TemplateResponse('site.html', {'request': request, 'msg': msg})

## Logout ##

@app.get('/crexusers/logout', name='logout')
def logout():
    response = RedirectResponse(url='/crexusers/', status_code=303)
    response.delete_cookie('access_token')
    return response

## Register ##

@app.api_route('/crexusers/register', methods=['GET', 'POST'], name='register')
def register(
    request: Request,
    username: Annotated[str | None, Form()] = None,
    name: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    email: Annotated[str | None, Form()] = None,
):
    msg = ''

    if request.method == 'POST':
        if username and name and password and email:
            account = get_user(username)
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            else:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                create_user(username, name, password_hash, email)
                msg = 'You have successfully registered!'
        else:
            msg = 'Please fill out the form!'

    return templates.TemplateResponse('register.html', {'request': request, 'msg': msg})

## Home ##

@app.get('/crexusers/home', name='home')
def home(
    request: Request,
    current_user: Annotated[UserContext, Depends(get_current_user)],
):
    balance = get_balance(current_user.id)
    return templates.TemplateResponse('home.html', {
        'request': request,
        'name': current_user.name,
        'balance': balance,
        'script_root': request.scope.get('root_path', ''),
    })

## Predict ##

@app.post('/crexusers/predict', name='predict', response_model=PredictResponse)
def predict(
    body: PredictRequest,
    current_user: Annotated[UserContext, Depends(get_current_user_api)],
):
    answer = communicate(body.message, id=current_user.id, name=current_user.name)
    return PredictResponse(answer=answer)
