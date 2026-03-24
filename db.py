#
# File: db.py
# Author: Daniel Oliveira
#

### SQLAlchemy ORM Database Layer ###

from __future__ import annotations

import json
import os

import bcrypt
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crexusers.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False)
    balance = Column(Integer, nullable=False, default=0)


class Intent(Base):
    __tablename__ = "intents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(100), nullable=False, unique=True)


class Pattern(Base):
    __tablename__ = "patterns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    intent_id = Column(Integer, ForeignKey("intents.id"), nullable=False)
    text = Column(String(500), nullable=False)


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    intent_id = Column(Integer, ForeignKey("intents.id"), nullable=False)
    text = Column(String(1000), nullable=False)


def removeUser(user: str) -> None:
    with SessionLocal() as session:
        u = session.query(User).filter_by(username=user).first()
        if u:
            session.delete(u)
            session.commit()


def updateBalance(id: int, new: int, flag: bool) -> None:
    with SessionLocal() as session:
        u = session.query(User).filter_by(id=id).first()
        if u:
            if flag:
                u.balance += new
            else:
                u.balance = max(0, u.balance - new)
            session.commit()


def updatePassword(id: int, new: str) -> None:
    with SessionLocal() as session:
        u = session.query(User).filter_by(id=id).first()
        if u:
            u.password = new
            session.commit()


def updateEmail(id: int, new: str) -> None:
    with SessionLocal() as session:
        u = session.query(User).filter_by(id=id).first()
        if u:
            u.email = new
            session.commit()


def get_user(username: str) -> dict | None:
    with SessionLocal() as session:
        u = session.query(User).filter_by(username=username).first()
        if u is None:
            return None
        return {
            "id": u.id,
            "username": u.username,
            "name": u.name,
            "password": u.password,
            "email": u.email,
            "balance": u.balance,
        }


def create_user(username: str, name: str, password_hash: str, email: str) -> None:
    with SessionLocal() as session:
        user = User(username=username, name=name, password=password_hash, email=email, balance=0)
        session.add(user)
        session.commit()


def get_balance(user_id: int) -> int:
    with SessionLocal() as session:
        u = session.query(User).filter_by(id=user_id).first()
        return u.balance if u else 0


def load_intents_from_db() -> dict:
    """Return intents in the same structure as intents.json."""
    with SessionLocal() as session:
        result = []
        for intent in session.query(Intent).all():
            patterns = [p.text for p in session.query(Pattern).filter_by(intent_id=intent.id).all()]
            answers = [a.text for a in session.query(Answer).filter_by(intent_id=intent.id).all()]
            result.append({"tag": intent.tag, "patterns": patterns, "answers": answers})
    return {"intents": result}


def initializeDB() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    with SessionLocal() as session:
        if not session.query(User).filter_by(username="daniel").first():
            password_hash = bcrypt.hashpw(b"pass1", bcrypt.gensalt()).decode("utf-8")
            session.add(User(
                username="daniel",
                name="Daniel Oliveira",
                password=password_hash,
                email="danielsoliveira@ua.pt",
                balance=0,
            ))
            session.commit()

        if session.query(Intent).count() == 0:
            with open("intents.json") as f:
                data = json.load(f)
            seen_tags: set[str] = set()
            for item in data["intents"]:
                if item["tag"] in seen_tags:
                    continue
                seen_tags.add(item["tag"])
                intent = Intent(tag=item["tag"])
                session.add(intent)
                session.flush()
                for p in item["patterns"]:
                    session.add(Pattern(intent_id=intent.id, text=p))
                for a in item["answers"]:
                    session.add(Answer(intent_id=intent.id, text=a))
            session.commit()

## Run directly to check database ##

def main() -> None:
    with SessionLocal() as session:
        for u in session.query(User).all():
            print(u.id, u.username, u.name, u.balance)


if __name__ == "__main__":
    main()
