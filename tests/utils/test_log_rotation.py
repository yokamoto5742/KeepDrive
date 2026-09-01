import configparser
import logging
from collections.abc import Iterator
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import pytest

from utils.log_rotation import _load_config_or_defaults, setup_logging


@pytest.fixture
def isolated_root_logger() -> Iterator[logging.Logger]:
    """テスト間でハンドラが積み上がらないよう、ルートロガーを退避する。"""
    root_logger = logging.getLogger()
    saved = list(root_logger.handlers)
    root_logger.handlers.clear()
    yield root_logger
    for handler in root_logger.handlers:
        handler.close()
    root_logger.handlers[:] = saved


def build_config(log_directory: Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config['LOGGING'] = {'log_directory': str(log_directory)}
    return config


def added_handlers(
    root_logger: logging.Logger, log_directory: Path
) -> list[type[logging.Handler]]:
    """setup_loggingが追加したハンドラの種類を返す（pytest側のハンドラは除く）。"""
    before = [id(handler) for handler in root_logger.handlers]
    setup_logging(build_config(log_directory))
    return [
        type(handler)
        for handler in root_logger.handlers
        if id(handler) not in before
    ]


def test_setup_logging_skips_console_handler_without_stdout(
    isolated_root_logger: logging.Logger, tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch
) -> None:
    # pythonw.exe 起動ではsys.stdoutがNoneになり、書き込みが例外になる
    monkeypatch.setattr('utils.log_rotation.sys.stdout', None)

    assert added_handlers(isolated_root_logger, tmp_path) == [
        TimedRotatingFileHandler
    ]


def test_setup_logging_adds_console_handler_with_stdout(
    isolated_root_logger: logging.Logger, tmp_path: Path
) -> None:
    assert added_handlers(isolated_root_logger, tmp_path) == [
        TimedRotatingFileHandler,
        logging.StreamHandler,
    ]


def test_load_config_or_defaults_falls_back_when_config_is_missing(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    def raise_missing() -> configparser.ConfigParser:
        raise FileNotFoundError('config.ini')

    monkeypatch.setattr('utils.log_rotation.load_config', raise_missing)

    # 設定が読めなくてもログだけは初期化できないと、失敗の記録が残らない
    assert _load_config_or_defaults().sections() == []
