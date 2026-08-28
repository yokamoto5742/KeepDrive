import logging
from urllib.parse import quote

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from app.constants import (
    DOCS_URL_GLOB,
    KEEP_CLOSE_NOTE_LABEL,
    KEEP_COPY_TO_DOCS_LABEL,
    KEEP_LOGIN_URL_PREFIX,
    KEEP_MORE_MENU_LABEL,
    KEEP_NOTE_BODY_LABEL,
    KEEP_NOTE_CARD_SELECTOR,
    KEEP_OPEN_COPIED_DOC_LABEL,
    KEEP_SEARCH_URL,
    MSG_COPIED_DOC_NOT_OPENED,
    MSG_KEEP_LOGIN_REQUIRED,
    MSG_MEMO_BODY_CLEARED,
    MSG_MEMO_BODY_NOT_CLEARED,
    MSG_MEMO_COPIED,
    MSG_MEMO_NOT_FOUND,
)

logger = logging.getLogger(__name__)


def copy_note_to_google_docs(page: Page, title: str) -> str:
    """指定タイトルのメモをKeepの「Googleドキュメントにコピー」で複製し、URLを返す。"""
    card = _find_note_card(page, title)

    card.hover()
    card.get_by_role('button', name=KEEP_MORE_MENU_LABEL).click()
    page.get_by_role('menuitem', name=KEEP_COPY_TO_DOCS_LABEL).click()

    copied_url = _read_copied_document_url(page, title)
    logger.info(MSG_MEMO_COPIED.format(title=title))
    return copied_url


def clear_note_body(page: Page, title: str) -> None:
    """メモを開いて本文だけを削除する（次回の登録に備えてタイトルは残す）。"""
    card = _find_note_card(page, title)
    card.click()

    body = page.get_by_role('textbox', name=KEEP_NOTE_BODY_LABEL)
    body.wait_for(state='visible')
    body.click()
    # フォーカスは本文のテキストボックス内にあるため、タイトルは選択されない
    page.keyboard.press('Control+A')
    page.keyboard.press('Delete')
    if body.inner_text().strip():
        raise RuntimeError(MSG_MEMO_BODY_NOT_CLEARED.format(title=title))

    page.get_by_role('button', name=KEEP_CLOSE_NOTE_LABEL).click()
    logger.info(MSG_MEMO_BODY_CLEARED.format(title=title))


def _find_note_card(page: Page, title: str) -> Locator:
    """タイトルで検索し、該当するメモカードを返す。"""
    page.goto(KEEP_SEARCH_URL.format(query=quote(title)))
    if page.url.startswith(KEEP_LOGIN_URL_PREFIX):
        raise ConnectionError(MSG_KEEP_LOGIN_REQUIRED)

    card = page.locator(KEEP_NOTE_CARD_SELECTOR).filter(
        has=page.get_by_text(title, exact=True)
    ).first
    try:
        card.wait_for(state='visible')
    except PlaywrightTimeoutError as e:
        raise LookupError(MSG_MEMO_NOT_FOUND.format(title=title)) from e

    return card


def _read_copied_document_url(page: Page, title: str) -> str:
    """コピー完了通知の「開く」から新しいタブを開き、URLを取得して閉じる。"""
    try:
        with page.context.expect_page() as copied_page_info:
            page.get_by_role('button', name=KEEP_OPEN_COPIED_DOC_LABEL).click()
    except PlaywrightTimeoutError as e:
        raise LookupError(
            MSG_COPIED_DOC_NOT_OPENED.format(
                label=KEEP_OPEN_COPIED_DOC_LABEL, title=title
            )
        ) from e

    copied_page = copied_page_info.value
    copied_page.wait_for_url(DOCS_URL_GLOB)
    copied_url = copied_page.url
    copied_page.close()
    return copied_url
