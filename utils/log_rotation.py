import configparser
import logging
import re
import sys
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Final

from app.constants import (
    CONFIG_SECTION_LOGGING,
    LOG_CONSOLE_DATE_FORMAT,
    LOG_CONSOLE_FORMAT,
    LOG_FILE_FORMAT,
    LOG_ROTATION_SUFFIX,
    MSG_INVALID_LOG_LEVEL,
    MSG_LOG_FILE_DELETE_FAILED,
    MSG_LOG_FILE_DELETED,
    MSG_LOG_INITIALIZED,
)
from utils.config_manager import load_config

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent


def _load_config_or_defaults() -> configparser.ConfigParser:
    """設定を読めなくてもログだけは初期化できるよう、既定値のまま継続する。"""
    try:
        return load_config()
    except (OSError, configparser.Error):
        return configparser.ConfigParser()


def setup_logging(config: configparser.ConfigParser | None = None) -> None:
    if config is None:
        config = _load_config_or_defaults()

    section = CONFIG_SECTION_LOGGING
    project_name = config.get(section, 'project_name', fallback='KeepDrive')
    retention_days = config.getint(section, 'log_retention_days', fallback=7)
    log_directory = _resolve_log_directory(
        config.get(section, 'log_directory', fallback='logs')
    )
    log_directory.mkdir(parents=True, exist_ok=True)
    log_file = log_directory / f'{project_name}.log'

    root_logger = logging.getLogger()
    root_logger.setLevel(_resolve_level(config.get(section, 'log_level', fallback='INFO')))
    for handler in _build_handlers(log_file):
        root_logger.addHandler(handler)

    cleanup_old_logs(log_directory, retention_days, project_name)
    logging.info(MSG_LOG_INITIALIZED.format(path=log_file))


def _resolve_log_directory(log_directory: str) -> Path:
    """相対指定はプロジェクトルート基準で解決する。"""
    path = Path(log_directory)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _resolve_level(log_level: str) -> int:
    level = logging.getLevelNamesMapping().get(log_level.upper())
    if level is None:
        logging.warning(MSG_INVALID_LOG_LEVEL.format(level=log_level))
        return logging.INFO

    return level


def _build_handlers(log_file: Path) -> list[logging.Handler]:
    file_handler = TimedRotatingFileHandler(
        filename=log_file, when='midnight', backupCount=0, encoding='utf-8'
    )
    # suffixを差し替えるとハンドラ内部のextMatchと食い違い、backupCountによる
    # 自動削除が効かなくなる。古いログの削除はcleanup_old_logs()だけが担う。
    file_handler.suffix = LOG_ROTATION_SUFFIX
    file_handler.setFormatter(logging.Formatter(LOG_FILE_FORMAT))
    handlers: list[logging.Handler] = [file_handler]

    # pythonw.exe 起動ではsys.stdoutがNoneになるため、コンソールがある場合だけ追加する
    if sys.stdout is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(LOG_CONSOLE_FORMAT, datefmt=LOG_CONSOLE_DATE_FORMAT)
        )
        handlers.append(console_handler)

    return handlers


def cleanup_old_logs(
    log_directory: Path, retention_days: int, project_name: str
) -> None:
    """保持期間を過ぎたローテーション済みログを削除する。"""
    rotated = re.compile(
        rf'{re.escape(project_name)}\.log\.\d{{4}}-\d{{2}}-\d{{2}}\.log$'
    )
    expiration = datetime.now() - timedelta(days=retention_days)

    for log_file in log_directory.iterdir():
        if not rotated.match(log_file.name):
            continue
        try:
            if datetime.fromtimestamp(log_file.stat().st_mtime) <= expiration:
                log_file.unlink()
                logging.info(MSG_LOG_FILE_DELETED.format(name=log_file.name))
        except OSError as e:
            logging.error(
                MSG_LOG_FILE_DELETE_FAILED.format(name=log_file.name, error=e)
            )
