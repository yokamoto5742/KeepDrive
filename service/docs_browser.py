import logging
import re
import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from app.constants import (
    DIALOG_TIMEOUT_MS,
    DOCS_EDITOR_SELECTOR,
    DOCS_EXPORT_URL,
    DOCS_FILE_MENU_LABEL,
    DOCS_MOVE_TO_TRASH_LABEL,
    DOCS_SAVE_POLL_INTERVAL_SECONDS,
    DOCS_SAVE_POLL_MAX_ATTEMPTS,
    DOCS_URL_PATTERN,
    MSG_APPEND_NOT_SAVED,
    MSG_DOCUMENT_FETCH_FAILED,
    MSG_INVALID_DOCUMENT_URL,
)

logger = logging.getLogger(__name__)


def fetch_document_text(page: Page, document_url: str) -> str:
    """ログイン済みセッションのままテキスト形式でエクスポートし、本文を取得する。"""
    export_url = DOCS_EXPORT_URL.format(document_id=extract_document_id(document_url))
    response = page.request.get(export_url)
    if not response.ok:
        raise RuntimeError(
            MSG_DOCUMENT_FETCH_FAILED.format(status=response.status, url=document_url)
        )

    return _normalize_newlines(response.text())


def append_text(page: Page, document_url: str, text: str) -> None:
    """ドキュメント末尾へテキストを入力し、保存されたことを確認する。"""
    text_before_append = fetch_document_text(page, document_url)

    page.goto(document_url)
    editor = page.locator(DOCS_EDITOR_SELECTOR)
    editor.wait_for(state='visible')
    editor.click()
    page.keyboard.press('Control+End')
    _input_paragraphs(page, text)

    _wait_until_saved(page, document_url, text_before_append, text)


def move_to_trash(page: Page, document_url: str) -> None:
    """ファイルメニューからドキュメントをゴミ箱へ移動する（完全削除はしない）。"""
    page.goto(document_url)
    page.get_by_role('menuitem', name=DOCS_FILE_MENU_LABEL).click()
    page.get_by_role('menuitem', name=DOCS_MOVE_TO_TRASH_LABEL).click()
    _confirm_trash_dialog(page)


def extract_document_id(document_url: str) -> str:
    matched = re.search(DOCS_URL_PATTERN, document_url)
    if not matched:
        raise ValueError(MSG_INVALID_DOCUMENT_URL.format(url=document_url))

    return matched.group(1)


def _input_paragraphs(page: Page, text: str) -> None:
    """改行のみEnterキーで送り、段落を保ったまま入力する。"""
    for index, line in enumerate(text.split('\n')):
        if index:
            page.keyboard.press('Enter')
        if line:
            page.keyboard.insert_text(line)


def _wait_until_saved(
    page: Page, document_url: str, text_before_append: str, appended_text: str
) -> None:
    """エクスポート結果で保存反映を確認する（未保存のままコピーを消さないため）。"""
    expected = appended_text.strip('\n')

    for _ in range(DOCS_SAVE_POLL_MAX_ATTEMPTS):
        time.sleep(DOCS_SAVE_POLL_INTERVAL_SECONDS)
        current_text = fetch_document_text(page, document_url)
        if current_text != text_before_append and expected in current_text:
            return

    raise TimeoutError(MSG_APPEND_NOT_SAVED.format(url=document_url))


def _confirm_trash_dialog(page: Page) -> None:
    """確認ダイアログが出た場合のみ実行ボタンを押す。"""
    try:
        page.get_by_role('button', name=DOCS_MOVE_TO_TRASH_LABEL).click(
            timeout=DIALOG_TIMEOUT_MS
        )
    except PlaywrightTimeoutError:
        pass


def _normalize_newlines(text: str) -> str:
    return text.replace('\ufeff', '').replace('\r\n', '\n')
