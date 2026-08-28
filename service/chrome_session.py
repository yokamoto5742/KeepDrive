import logging
from collections.abc import Iterator
from contextlib import contextmanager

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright

from app.constants import (
    BROWSER_TIMEOUT_MS,
    CHROME_CDP_URL,
    MSG_CHROME_CONNECT_FAILED,
    MSG_CHROME_CONNECTED,
)

logger = logging.getLogger(__name__)


@contextmanager
def open_chrome_page() -> Iterator[Page]:
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
