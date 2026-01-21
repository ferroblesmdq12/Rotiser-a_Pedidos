# src/core/auth.py

import hashlib
from dataclasses import dataclass
from typing import Optional, Dict

import streamlit as st

from src.core.config import Settings


@dataclass(frozen=True)
class User:
    username: str
    role: str


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def authenticate(settings: Settings, username: str, password: str) -> Optional[User]:
    uname = (username or "").strip()
    pwd = (password or "").strip()

    record = settings.users.get(uname)
    if not record:
        return None

    if sha256(pwd) != record.password_sha256:
        return None

    return User(username=record.username, role=record.role)


def set_user_session(user: User) -> None:
    st.session_state["user"] = {"username": user.username, "role": user.role}


def get_user_session() -> Optional[Dict[str, str]]:
    return st.session_state.get("user")


def logout() -> None:
    st.session_state.pop("user", None)


def require_login() -> Dict[str, str]:
    user = get_user_session()
    if not user:
        st.stop()
    return user


def can_edit_estado(role: str) -> bool:
    # Both roles can edit estado in MVP
    return role in ("admin", "owner")
