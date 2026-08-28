import logging
import time
from typing import Any

from playwright.sync_api import Page

from app.constants import (
    DRIVE_POLL_INTERVAL_SECONDS,
    DRIVE_POLL_MAX_ATTEMPTS,
    MSG_COPIED_DOC_NOT_FOUND,
    MSG_COPIED_DOC_TRASHED,
    MSG_MEMO_START,
    MSG_MERGE_SUCCESS,
    MSG_MERGE_TARGET_NOT_FOUND,
)
from service.docs_client import append_text, extract_text
from service.drive_client import find_document_ids_by_name, trash_file
from service.keep_browser import copy_note_to_google_docs

logger = logging.getLogger(__name__)


def merge_memo(page: Page, drive: Any, docs: Any, title: str) -> None:
    """メモ1件をコピーし、同名の既存ドキュメントがあれば結合してコピーを削除する。"""
    logger.info(MSG_MEMO_START.format(title=title))

    existing_ids = find_document_ids_by_name(drive, title)
    copy_note_to_google_docs(page, title)
    copied_id = _wait_for_copied_document(drive, title, existing_ids)

    if not existing_ids:
        logger.info(MSG_MERGE_TARGET_NOT_FOUND.format(title=title))
        return

    copied_text = _normalize_append_text(extract_text(docs, copied_id))
    append_text(docs, existing_ids[0], copied_text)
    logger.info(MSG_MERGE_SUCCESS.format(title=title))

    # 結合が成功した場合のみコピーを削除する（順序を入れ替えるとデータ消失につながる）
    trash_file(drive, copied_id)
    logger.info(MSG_COPIED_DOC_TRASHED.format(title=title))


def _wait_for_copied_document(
    drive: Any, title: str, existing_ids: list[str]
) -> str:
    """Driveへのコピー反映を待ち、新しく増えたドキュメントのIDを返す。"""
    known_ids = set(existing_ids)

    for _ in range(DRIVE_POLL_MAX_ATTEMPTS):
        time.sleep(DRIVE_POLL_INTERVAL_SECONDS)
        new_ids = [
            file_id
            for file_id in find_document_ids_by_name(drive, title)
            if file_id not in known_ids
        ]
        if new_ids:
            return new_ids[-1]

    raise LookupError(MSG_COPIED_DOC_NOT_FOUND.format(title=title))


def _normalize_append_text(text: str) -> str:
    """末尾の余分な改行を1つに揃え、既存ドキュメントへ追記できる形にする。"""
    return text.rstrip('\n') + '\n'
