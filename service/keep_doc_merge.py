import logging

from playwright.sync_api import Page

from app.constants import (
    MSG_COPIED_DOC_TRASHED,
    MSG_MEMO_START,
    MSG_MERGE_SUCCESS,
)
from service.docs_browser import append_text, fetch_document_text, move_to_trash
from service.keep_browser import copy_note_to_google_docs

logger = logging.getLogger(__name__)


def merge_memo(page: Page, title: str, destination_url: str) -> None:
    """メモ1件をコピーし、結合先ドキュメントへ追記してコピーを削除する。"""
    logger.info(MSG_MEMO_START.format(title=title))

    copied_url = copy_note_to_google_docs(page, title)
    copied_text = _to_appendable_text(fetch_document_text(page, copied_url))

    append_text(page, destination_url, copied_text)
    logger.info(MSG_MERGE_SUCCESS.format(title=title))

    # 追記の保存を確認できた場合のみ削除する（順序を入れ替えるとデータ消失につながる）
    move_to_trash(page, copied_url)
    logger.info(MSG_COPIED_DOC_TRASHED.format(title=title))


def _to_appendable_text(text: str) -> str:
    """前後の余分な改行を落とし、既存本文と段落を分けて追記できる形にする。"""
    return '\n' + text.strip('\n')
