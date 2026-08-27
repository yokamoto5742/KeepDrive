import logging
from typing import Any, NamedTuple

from gkeepapi.node import List as KeepList
from gkeepapi.node import ListItem

from app.constants import (
    MSG_APPEND_SUCCESS,
    MSG_CLEAR_SUCCESS,
    MSG_LIST_NOT_FOUND,
    MSG_NOTE_FAILED,
    MSG_NOTE_START,
    MSG_TARGET_LISTS_ALL,
    MSG_TARGET_LISTS_SELECTED,
)
from service.docs_client import append_text
from service.drive_client import find_or_create_document, find_or_create_folder
from service.keep_client import clear_list_items

logger = logging.getLogger(__name__)


class SyncResult(NamedTuple):
    success_count: int
    failure_count: int


def filter_target_notes(
    notes: list[KeepList], target_names: list[str]
) -> list[KeepList]:
    """設定で指定されたリスト名のみに絞り込む。未指定なら全件を返す。"""
    if not target_names:
        logger.info(MSG_TARGET_LISTS_ALL)
        return notes

    logger.info(MSG_TARGET_LISTS_SELECTED.format(names='、'.join(target_names)))
    filtered = [note for note in notes if note.title in target_names]

    missing = [name for name in target_names if name not in {n.title for n in notes}]
    if missing:
        logger.warning(MSG_LIST_NOT_FOUND.format(names='、'.join(missing)))

    return filtered


def sort_items(items: list[ListItem]) -> list[ListItem]:
    """更新日時の降順、同時刻はテキスト昇順で並べ替える（仕様書 §6.1）。"""
    by_text = sorted(items, key=lambda item: item.text)
    return sorted(by_text, key=lambda item: item.timestamps.updated, reverse=True)


def build_append_text(items: list[ListItem]) -> str:
    """アイテム名のみを1行ずつ並べた追記テキストを生成する（仕様書 §6.2）。"""
    return ''.join(f'{item.text}\n' for item in sort_items(items))


def sync_notes(notes: list[KeepList], drive: Any, docs: Any) -> SyncResult:
    """各リストメモをDriveへ追記し、成功したメモのみ空にする（仕様書 §5-4）。"""
    success_count = 0
    failure_count = 0

    for note in notes:
        if _sync_note(note, drive, docs):
            success_count += 1
        else:
            failure_count += 1

    return SyncResult(success_count, failure_count)


def _sync_note(note: KeepList, drive: Any, docs: Any) -> bool:
    """1件のリストメモを処理する。1件の失敗で全体を止めないため例外を握りつぶす。"""
    items = note.items
    logger.info(MSG_NOTE_START.format(title=note.title, count=len(items)))

    try:
        text = build_append_text(items)
        folder_id = find_or_create_folder(drive, note.title)
        document_id = find_or_create_document(drive, note.title, folder_id)
        append_text(docs, document_id, text)
        logger.info(MSG_APPEND_SUCCESS.format(title=note.title, count=len(items)))

        clear_list_items(note)
        logger.info(MSG_CLEAR_SUCCESS.format(title=note.title))
        return True
    except Exception as e:
        logger.error(MSG_NOTE_FAILED.format(title=note.title, error=e))
        return False
