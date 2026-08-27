import json
import logging
import os

import gkeepapi
from gkeepapi.node import List as KeepList

from app.constants import (
    ENV_KEEP_EMAIL,
    ENV_KEEP_MASTER_TOKEN,
    MSG_ENV_KEY_MISSING,
    MSG_KEEP_AUTH_SUCCESS,
    MSG_KEEP_STATE_LOAD_FAILED,
    MSG_KEEP_STATE_SAVE_FAILED,
)
from app.paths import KEEP_STATE_PATH

logger = logging.getLogger(__name__)


def authenticate_keep() -> gkeepapi.Keep:
    """マスタートークンでKeepにログインする。状態キャッシュがあれば差分同期する。"""
    email = _require_env(ENV_KEEP_EMAIL)
    master_token = _require_env(ENV_KEEP_MASTER_TOKEN)

    keep = gkeepapi.Keep()
    keep.authenticate(email, master_token, state=_load_state())
    logger.info(MSG_KEEP_AUTH_SUCCESS.format(email=email))
    return keep


def save_state(keep: gkeepapi.Keep) -> None:
    """次回の差分同期用に状態キャッシュを書き出す。失敗しても処理は継続する。"""
    try:
        KEEP_STATE_PATH.write_text(
            json.dumps(keep.dump()), encoding='utf-8'
        )
    except (OSError, TypeError, ValueError) as e:
        logger.warning(MSG_KEEP_STATE_SAVE_FAILED.format(error=e))


def fetch_list_notes(keep: gkeepapi.Keep) -> list[KeepList]:
    """タイトルとアイテムを持つ有効なリストメモを抽出する（仕様書 §5-3）。"""
    return [
        node
        for node in keep.all()
        if isinstance(node, KeepList)
        and not node.trashed
        and not node.archived
        and node.title
        and len(node.items) >= 1
    ]


def clear_list_items(note: KeepList) -> None:
    """リストメモ内のアイテムをすべて削除して空にする（仕様書 §5-4-e）。"""
    for item in note.items:
        item.delete()


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(MSG_ENV_KEY_MISSING.format(key=key))
    return value


def _load_state() -> dict | None:
    if not KEEP_STATE_PATH.exists():
        return None
    try:
        return json.loads(KEEP_STATE_PATH.read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        logger.warning(MSG_KEEP_STATE_LOAD_FAILED.format(error=e))
        return None
