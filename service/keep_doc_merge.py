import logging

from playwright.sync_api import Page

from app.constants import (
    MSG_COPIED_DOC_TRASHED,
    MSG_DUPLICATE_LINES_SKIPPED,
    MSG_MEMO_BODY_EMPTY,
    MSG_MERGE_SUCCESS,
    MSG_NO_NEW_CONTENT,
)
from service.docs_browser import append_text, fetch_document_text, move_to_trash
from service.keep_browser import (
    clear_note_body,
    copy_note_to_google_docs,
    read_note_body,
)

logger = logging.getLogger(__name__)


def merge_memo(page: Page, title: str, destination_url: str) -> None:
    """メモ1件をコピーし、重複を除いて追記したうえでコピーとメモ本文を消す。"""
    if not read_note_body(page, title).strip():
        logger.info(MSG_MEMO_BODY_EMPTY.format(title=title))
        return

    copied_url = copy_note_to_google_docs(page, title)
    copied_text = fetch_document_text(page, copied_url)
    destination_text = fetch_document_text(page, destination_url)
    new_text = _remove_duplicate_lines(copied_text, destination_text)
    _log_skipped_duplicates(title, copied_text, new_text)

    if new_text:
        append_text(page, destination_url, _with_separator(destination_text, new_text))
        logger.info(MSG_MERGE_SUCCESS.format(title=title))
    else:
        logger.info(MSG_NO_NEW_CONTENT.format(title=title))

    # 追記の保存を確認できた場合のみ削除する（順序を入れ替えるとデータ消失につながる）
    move_to_trash(page, copied_url)
    logger.info(MSG_COPIED_DOC_TRASHED.format(title=title))

    clear_note_body(page, title)


def _with_separator(destination_text: str, new_text: str) -> str:
    """既存本文があるときだけ区切りの改行を付ける（空のドキュメントの先頭に空行を作らない）。"""
    return '\n' + new_text if destination_text.strip() else new_text


def _remove_duplicate_lines(copied_text: str, destination_text: str) -> str:
    """結合先に既にある行と、コピー内で重複する行を除いたテキストを返す。"""
    seen = {line.strip() for line in destination_text.split('\n') if line.strip()}
    kept: list[str] = []
    for line in copied_text.split('\n'):
        key = line.strip()
        if not key:
            kept.append(line)  # 空行は段落の区切りとして残す
            continue
        if key in seen:
            continue
        seen.add(key)
        kept.append(line)

    return '\n'.join(kept).strip('\n')


def _log_skipped_duplicates(title: str, copied_text: str, new_text: str) -> None:
    removed = _count_content_lines(copied_text) - _count_content_lines(new_text)
    if removed:
        logger.info(MSG_DUPLICATE_LINES_SKIPPED.format(title=title, count=removed))


def _count_content_lines(text: str) -> int:
    return len([line for line in text.split('\n') if line.strip()])
