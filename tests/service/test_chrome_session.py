import subprocess
from unittest.mock import MagicMock

import pytest
from playwright.sync_api import Error as PlaywrightError

from app.constants import CHROME_CDP_URL
from service.chrome_session import (
    _close_session,
    connect_chrome,
    find_chrome_executable,
    launch_chrome,
)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('service.chrome_session.time.sleep', lambda _: None)


def build_playwright(*connect_results: object) -> MagicMock:
    """connect_over_cdpの呼び出し順に結果（例外またはBrowser）を返す。"""
    playwright = MagicMock()
    playwright.chromium.connect_over_cdp.side_effect = list(connect_results)
    return playwright


def test_connect_chrome_uses_running_chrome(monkeypatch: pytest.MonkeyPatch) -> None:
    launched = MagicMock()
    monkeypatch.setattr('service.chrome_session.launch_chrome', launched)
    browser = MagicMock()
    playwright = build_playwright(browser)

    assert connect_chrome(playwright) == (browser, None)
    playwright.chromium.connect_over_cdp.assert_called_once_with(CHROME_CDP_URL)
    launched.assert_not_called()


def test_connect_chrome_launches_and_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    launched = MagicMock()
    monkeypatch.setattr('service.chrome_session.launch_chrome', launched)
    browser = MagicMock()
    playwright = build_playwright(
        PlaywrightError('ECONNREFUSED'), PlaywrightError('ECONNREFUSED'), browser
    )

    assert connect_chrome(playwright) == (browser, launched.return_value)
    launched.assert_called_once_with()


def test_connect_chrome_raises_when_launch_does_not_help(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr('service.chrome_session.launch_chrome', MagicMock())
    monkeypatch.setattr('service.chrome_session.CHROME_LAUNCH_MAX_ATTEMPTS', 2)
    playwright = build_playwright(*[PlaywrightError('ECONNREFUSED')] * 3)

    with pytest.raises(ConnectionError, match=CHROME_CDP_URL):
        connect_chrome(playwright)


def test_connect_chrome_kills_launched_chrome_when_it_never_connects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launched = MagicMock()
    monkeypatch.setattr('service.chrome_session.launch_chrome', launched)
    monkeypatch.setattr('service.chrome_session.CHROME_LAUNCH_MAX_ATTEMPTS', 2)
    playwright = build_playwright(*[PlaywrightError('ECONNREFUSED')] * 3)

    with pytest.raises(ConnectionError):
        connect_chrome(playwright)

    # 起動したヘッドレスChromeを孤児プロセスとして残さない
    launched.return_value.kill.assert_called_once()


def test_find_chrome_executable_returns_existing_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        'service.chrome_session.CHROME_EXECUTABLE_PATHS', (r'C:\missing.exe', r'C:\chrome.exe')
    )
    monkeypatch.setattr(
        'service.chrome_session.Path.is_file',
        lambda self: str(self) == r'C:\chrome.exe',
    )

    assert find_chrome_executable() == r'C:\chrome.exe'


def test_find_chrome_executable_raises_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        'service.chrome_session.CHROME_EXECUTABLE_PATHS', (r'C:\missing.exe',)
    )
    monkeypatch.setattr('service.chrome_session.Path.is_file', lambda self: False)

    with pytest.raises(FileNotFoundError):
        find_chrome_executable()


def test_launch_chrome_passes_remote_debugging_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        'service.chrome_session.find_chrome_executable', lambda: r'C:\chrome.exe'
    )
    popen = MagicMock()
    monkeypatch.setattr('service.chrome_session.subprocess.Popen', popen)

    launch_chrome()

    args = popen.call_args.args[0]
    assert args[0] == r'C:\chrome.exe'
    assert '--remote-debugging-port=9222' in args
    # デフォルトプロファイルでは--remote-debugging-portが無視されるため専用ディレクトリを渡す
    user_data_dir_arg = next(a for a in args if a.startswith('--user-data-dir='))
    assert '%' not in user_data_dir_arg


def test_launch_chrome_runs_headless(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        'service.chrome_session.find_chrome_executable', lambda: r'C:\chrome.exe'
    )
    popen = MagicMock()
    monkeypatch.setattr('service.chrome_session.subprocess.Popen', popen)

    assert launch_chrome() is popen.return_value
    assert '--headless=new' in popen.call_args.args[0]


def test_close_session_terminates_launched_chrome() -> None:
    page, browser, process = MagicMock(), MagicMock(), MagicMock()

    _close_session(page, browser, process)

    cdp_session = page.context.new_cdp_session.return_value
    cdp_session.send.assert_called_once_with('Browser.close')
    browser.close.assert_called_once()
    process.wait.assert_called_once()


def test_close_session_kills_chrome_when_it_does_not_exit() -> None:
    page, browser, process = MagicMock(), MagicMock(), MagicMock()
    process.wait.side_effect = subprocess.TimeoutExpired(cmd='chrome', timeout=5)

    _close_session(page, browser, process)

    process.kill.assert_called_once()


def test_close_session_keeps_manually_started_chrome_running() -> None:
    page, browser = MagicMock(), MagicMock()

    _close_session(page, browser, None)

    page.close.assert_called_once()
    browser.close.assert_called_once()
    page.context.new_cdp_session.assert_not_called()
