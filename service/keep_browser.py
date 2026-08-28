import logging
from collections.abc import Iterator
from contextlib import contextmanager
from urllib.parse import quote

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from app.constants import (
    BROWSER_TIMEOUT_MS,
    CHROME_CDP_URL,
    KEEP_COPY_TO_DOCS_LABEL,
    KEEP_MORE_MENU_LABEL,
    KEEP_SEARCH_URL,
    MSG_CHROME_CONNECT_FAILED,
    MSG_CHROME_CONNECTED,
    MSG_MEMO_COPIED,
    MSG_MEMO_NOT_FOUND,
)

logger = logging.getLogger(__name__)


@contextmanager
def open_keep_page() -> Iterator[Page]:
    """起動済みローカルChromeにCDPで接続し、操作用のページを提供する。

    ログイン済みプロファイルをそのまま使うため、既存コンテキストを利用する。
    """
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.connect_over_cdp(CHROME_CDP_URL)
        except PlaywrightError as e:
            raise ConnectionError(
                MSG_CHROME_CONNECT_FAILED.format(url=CHROME_CDP_URL, error=e)
            ) from e

        logger.info(MSG_CHROME_CONNECTED.format(url=CHROME_CDP_URL))
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        page.set_default_timeout(BROWSER_TIMEOUT_MS)
        try:
            yield page
        finally:
            page.close()
            # CDP接続を切るだけで、ユーザーのChrome自体は終了しない
            browser.close()


def copy_note_to_google_docs(page: Page, title: str) -> None:
    """指定タイトルのメモをKeepの「Googleドキュメントにコピー」で複製する。"""
    page.goto(KEEP_SEARCH_URL.format(query=quote(title)))

    card = page.get_by_role('listitem').filter(
        has=page.get_by_text(title, exact=True)
    ).first
    try:
        card.wait_for(state='visible')
    except PlaywrightTimeoutError as e:
        raise LookupError(MSG_MEMO_NOT_FOUND.format(title=title)) from e

    card.hover()
    card.get_by_role('button', name=KEEP_MORE_MENU_LABEL).click()
    page.get_by_role('menuitem', name=KEEP_COPY_TO_DOCS_LABEL).click()
    logger.info(MSG_MEMO_COPIED.format(title=title))
