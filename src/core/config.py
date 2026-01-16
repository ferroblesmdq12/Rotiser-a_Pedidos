from dataclasses import dataclass
from typing import Dict, Any

import streamlit as st

from src.core.logging import get_logger

log = get_logger("config")


@dataclass(frozen=True)
class AppConfig:
    spreadsheet_id: str
    worksheet_name: str


@dataclass(frozen=True)
class UserRecord:
    username: str
    password_sha256: str
    role: str


@dataclass(frozen=True)
class Settings:
    app: AppConfig
    users: Dict[str, UserRecord]


def _require(path: str, obj: Dict[str, Any]):
    """
    Require a key exists in obj. path is just for error message clarity.
    """
    if obj is None:
        raise ValueError(f"Missing config section: {path}")


def load_settings() -> Settings:
    secrets = st.secrets

    # Validate GCP service account block exists
    _require("gcp_service_account", secrets.get("gcp_service_account"))

    app = secrets.get("app")
    _require("app", app)

    spreadsheet_id = str(app.get("spreadsheet_id", "")).strip()
    worksheet_name = str(app.get("worksheet_name", "")).strip()

    if not spreadsheet_id:
        raise ValueError("Missing secrets: app.spreadsheet_id")
    if not worksheet_name:
        raise ValueError("Missing secrets: app.worksheet_name")

    users_block = secrets.get("users")
    _require("users", users_block)

    users: Dict[str, UserRecord] = {}
    for key, val in users_block.items():
        username = str(val.get("username", "")).strip()
        pwd = str(val.get("password_sha256", "")).strip()
        role = str(val.get("role", "owner")).strip()

        if not username or not pwd:
            raise ValueError(f"Invalid user record for users.{key}: username/password missing")

        users[username] = UserRecord(username=username, password_sha256=pwd, role=role)

    cfg = Settings(app=AppConfig(spreadsheet_id=spreadsheet_id, worksheet_name=worksheet_name), users=users)
    log.info("Settings loaded OK")
    return cfg
