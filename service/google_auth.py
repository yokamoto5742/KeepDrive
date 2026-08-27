import logging
from typing import Any, cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.constants import (
    GOOGLE_API_SCOPES,
    MSG_CREDENTIALS_NOT_FOUND,
    MSG_OAUTH_BROWSER_START,
    MSG_TOKEN_SAVED,
)
from app.paths import CREDENTIALS_PATH, TOKEN_PATH

logger = logging.getLogger(__name__)


def load_credentials() -> Credentials:
    """token.jsonを再利用し、無効な場合のみブラウザ認証を行う（仕様書 §4.2）。"""
    credentials = _load_saved_credentials()

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        credentials = _run_installed_app_flow()

    _save_credentials(credentials)
    return credentials


def build_drive_service(credentials: Credentials) -> Any:
    return build('drive', 'v3', credentials=credentials, cache_discovery=False)


def build_docs_service(credentials: Credentials) -> Any:
    return build('docs', 'v1', credentials=credentials, cache_discovery=False)


def _load_saved_credentials() -> Credentials | None:
    if not TOKEN_PATH.exists():
        return None
    return Credentials.from_authorized_user_file(str(TOKEN_PATH), GOOGLE_API_SCOPES)


def _run_installed_app_flow() -> Credentials:
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            MSG_CREDENTIALS_NOT_FOUND.format(path=CREDENTIALS_PATH)
        )

    logger.info(MSG_OAUTH_BROWSER_START)
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_PATH), GOOGLE_API_SCOPES
    )
    # デスクトップアプリのフローは常にoauth2のCredentialsを返す
    return cast(Credentials, flow.run_local_server(port=0))


def _save_credentials(credentials: Credentials) -> None:
    TOKEN_PATH.write_text(credentials.to_json(), encoding='utf-8')
    logger.info(MSG_TOKEN_SAVED.format(path=TOKEN_PATH))
