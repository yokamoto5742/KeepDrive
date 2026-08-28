import logging
from typing import Any

from app.constants import (
    DRIVE_DOCUMENT_MIME_TYPE,
    DRIVE_FOLDER_MIME_TYPE,
    MSG_DOCUMENT_CREATED,
    MSG_FOLDER_CREATED,
)

logger = logging.getLogger(__name__)

ROOT_FOLDER_ID = 'root'


def find_or_create_folder(drive: Any, name: str) -> str:
    """マイドライブ直下の同名フォルダを検索し、無ければ作成してIDを返す。"""
    folder_id = _find_file_id(drive, name, DRIVE_FOLDER_MIME_TYPE, ROOT_FOLDER_ID)
    if folder_id:
        return folder_id

    created = drive.files().create(
        body={
            'name': name,
            'mimeType': DRIVE_FOLDER_MIME_TYPE,
            'parents': [ROOT_FOLDER_ID],
        },
        fields='id',
    ).execute()
    logger.info(MSG_FOLDER_CREATED.format(name=name))
    return created['id']


def find_or_create_document(drive: Any, name: str, folder_id: str) -> str:
    """フォルダ内の同名ドキュメントを検索し、無ければ作成してIDを返す。"""
    document_id = _find_file_id(drive, name, DRIVE_DOCUMENT_MIME_TYPE, folder_id)
    if document_id:
        return document_id

    created = drive.files().create(
        body={
            'name': name,
            'mimeType': DRIVE_DOCUMENT_MIME_TYPE,
            'parents': [folder_id],
        },
        fields='id',
    ).execute()
    logger.info(MSG_DOCUMENT_CREATED.format(name=name))
    return created['id']


def find_document_ids_by_name(drive: Any, name: str) -> list[str]:
    """ドライブ全体から同名ドキュメントのIDを作成日時の昇順で返す。"""
    query = (
        f"mimeType='{DRIVE_DOCUMENT_MIME_TYPE}' "
        f"and name='{escape_query_value(name)}' "
        f"and trashed=false"
    )
    response = drive.files().list(
        q=query,
        fields='files(id)',
        orderBy='createdTime',
        pageSize=100,
    ).execute()

    return [file['id'] for file in response.get('files', [])]


def trash_file(drive: Any, file_id: str) -> None:
    """ファイルをゴミ箱へ移動する（完全削除はしない）。"""
    drive.files().update(fileId=file_id, body={'trashed': True}).execute()


def escape_query_value(value: str) -> str:
    """Drive検索クエリのリテラルに含まれる \\ と ' をエスケープする。"""
    return value.replace('\\', '\\\\').replace("'", "\\'")


def _find_file_id(
    drive: Any, name: str, mime_type: str, parent_id: str
) -> str | None:
    query = (
        f"mimeType='{mime_type}' "
        f"and name='{escape_query_value(name)}' "
        f"and '{parent_id}' in parents "
        f"and trashed=false"
    )
    response = drive.files().list(
        q=query,
        fields='files(id,name)',
        pageSize=1,
    ).execute()

    files = response.get('files', [])
    return files[0]['id'] if files else None
