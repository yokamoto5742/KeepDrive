from typing import Any

from app.constants import DRIVE_DOCUMENT_MIME_TYPE


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
