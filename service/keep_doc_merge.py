"""Keepメモを Google ドキュメントへコピーし、同名の既存ドキュメントへ結合する。

実行: .venv\\Scripts\\python.exe -m service.keep_doc_merge
事前に Chrome を --remote-debugging-port=9222 付きで起動し、Keepにログインしておく。
"""
import logging
import sys
import time
from typing import Any

from playwright.sync_api import Page

from app.constants import (
    DRIVE_POLL_INTERVAL_SECONDS,
    DRIVE_POLL_MAX_ATTEMPTS,
    MSG_COPIED_DOC_NOT_FOUND,
    MSG_COPIED_DOC_TRASHED,
    MSG_FATAL_ERROR,
    MSG_MEMO_MERGE_FAILED,
    MSG_MEMO_START,
    MSG_MERGE_COMPLETED,
    MSG_MERGE_START,
    MSG_MERGE_SUCCESS,
    MSG_MERGE_TARGET_NOT_FOUND,
    MSG_NO_TARGET_MEMO,
)
from service.docs_client import append_text, extract_text
from service.drive_client import find_document_ids_by_name, trash_file
from service.google_auth import build_docs_service, build_drive_service, load_credentials
from service.keep_browser import copy_note_to_google_docs, open_keep_page
from utils.config_manager import get_target_memo_titles, load_config
from utils.log_rotation import setup_logging

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

    trash_file(drive, copied_id)
    logger.info(MSG_COPIED_DOC_TRASHED.format(title=title))


def run() -> int:
    """設定された全メモを処理し、終了コードを返す。"""
    config = load_config()
    setup_logging(config)
    logger.info(MSG_MERGE_START)

    titles = get_target_memo_titles(config)
    if not titles:
        logger.warning(MSG_NO_TARGET_MEMO)
        return 1

    credentials = load_credentials()
    drive = build_drive_service(credentials)
    docs = build_docs_service(credentials)

    failure_count = 0
    with open_keep_page() as page:
        for title in titles:
            # 1件の失敗で残りのメモを止めない
            try:
                merge_memo(page, drive, docs, title)
            except Exception as e:
                logger.error(MSG_MEMO_MERGE_FAILED.format(title=title, error=e))
                failure_count += 1

    logger.info(
        MSG_MERGE_COMPLETED.format(
            success=len(titles) - failure_count, failure=failure_count
        )
    )
    return 1 if failure_count else 0


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


def main() -> int:
    try:
        return run()
    except Exception as e:
        logging.error(MSG_FATAL_ERROR.format(error=e), exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
