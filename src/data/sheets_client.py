# src/data/sheets_client.py
from functools import lru_cache
from typing import List

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


@lru_cache(maxsize=1)
def get_gspread_client() -> gspread.Client:
    sa_info = dict(st.secrets["gcp_service_account"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    return gspread.authorize(creds)


def open_worksheet(spreadsheet_id: str, worksheet_name: str) -> gspread.Worksheet:
    client = get_gspread_client()
    sh = client.open_by_key(spreadsheet_id)
    return sh.worksheet(worksheet_name)


def read_all_values(spreadsheet_id: str, worksheet_name: str) -> List[List[str]]:
    ws = open_worksheet(spreadsheet_id, worksheet_name)
    return ws.get_all_values()


def debug_sa_email() -> str:
    sa_info = dict(st.secrets["gcp_service_account"])
    return str(sa_info.get("client_email", ""))
