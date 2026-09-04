import logging
import os
import subprocess
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import Browser
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from playwright.sync_api import Playwright
from playwright.sync_api import sync_playwright

from app.constants import (
    BROWSER_TIMEOUT_MS,
    CHROME_CDP_URL,
    CHROME_CLOSE_TIMEOUT_SECONDS,
    CHROME_EXECUTABLE_PATHS,
    CHROME_LAUNCH_ARGS,
    CHROME_LAUNCH_MAX_ATTEMPTS,
    CHROME_LAUNCH_POLL_INTERVAL_SECONDS,
    CHROME_USER_DATA_DIR,
    MSG_CHROME_CLOSE_FAILED,
    MSG_CHROME_CLOSED,
    MSG_CHROME_CONNECT_FAILED,
    MSG_CHROME_CONNECTED,
    MSG_CHROME_LAUNCHING,
    MSG_CHROME_NOT_FOUND,
)

logger = logging.getLogger(__name__)


def find_chrome_executable() -> str:
    """インストール済みChromeの実行ファイルパスを返す。"""
    candidates = [os.path.expandvars(path) for path in CHROME_EXECUTABLE_PATHS]
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    raise FileNotFoundError(MSG_CHROME_NOT_FOUND.format(paths=' / '.join(candidates)))


def launch_chrome() -> subprocess.Popen[bytes]:
    """リモートデバッグを有効にしたChromeをヘッドレスの専用プロファイルで起動する。"""
    executable = find_chrome_executable()
    user_data_dir = os.path.expandvars(CHROME_USER_DATA_DIR)
    args = [arg.format(user_data_dir=user_data_dir) for arg in CHROME_LAUNCH_ARGS]
    logger.info(MSG_CHROME_LAUNCHING.format(path=executable))
    return subprocess.Popen([executable, *args])


def connect_chrome(
    playwright: Playwright,
) -> tuple[Browser, subprocess.Popen[bytes] | None]:
    """CDP接続する。未起動ならChromeを起動して接続できるまで待つ。

    自分で起動した場合のみプロセスを返す（終了してよいかの判断に使う）。
    """
    try:
        return playwright.chromium.connect_over_cdp(CHROME_CDP_URL), None
    except PlaywrightError as e:
        last_error: PlaywrightError = e

    process = launch_chrome()
    for _ in range(CHROME_LAUNCH_MAX_ATTEMPTS):
        time.sleep(CHROME_LAUNCH_POLL_INTERVAL_SECONDS)
        try:
            return playwright.chromium.connect_over_cdp(CHROME_CDP_URL), process
        except PlaywrightError as e:
            last_error = e

    # 接続できなかった起動済みChromeはヘッドレスで見えないまま残るため、ここで回収する
    process.kill()
    raise ConnectionError(
        MSG_CHROME_CONNECT_FAILED.format(url=CHROME_CDP_URL, error=last_error)
    ) from last_error


@contextmanager
def open_chrome_page() -> Iterator[Page]:
    """ローカルChromeにCDPで接続し、操作用のページを提供する。

    ログイン済みプロファイルをそのまま使うため、既存コンテキストを利用する。
    """
    with sync_playwright() as playwright:
        browser, process = connect_chrome(playwright)

        logger.info(MSG_CHROME_CONNECTED.format(url=CHROME_CDP_URL))
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        page.set_default_timeout(BROWSER_TIMEOUT_MS)
        try:
            yield page
        finally:
            _close_session(page, browser, process)


def _close_session(
    page: Page, browser: Browser, process: subprocess.Popen[bytes] | None
) -> None:
    """自分で起動したChromeは終了する。手動起動のChromeは切断だけに留める。"""
    if process is None:
        page.close()
        browser.close()
        return

    # connect_over_cdpのbrowser.close()は切断のみなので、CDP経由で本体を終了させる
    try:
        page.context.new_cdp_session(page).send('Browser.close')
    except PlaywrightError:
        pass
    browser.close()
    _terminate(process)


def _terminate(process: subprocess.Popen[bytes]) -> None:
    """Chromeプロセスの終了を待ち、残っていれば強制終了する。"""
    try:
        process.wait(timeout=CHROME_CLOSE_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
    except OSError as e:
        logger.warning(MSG_CHROME_CLOSE_FAILED.format(error=e))
        return

    logger.info(MSG_CHROME_CLOSED)
