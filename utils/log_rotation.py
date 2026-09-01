import configparser
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

from utils.config_manager import load_config


def _load_config_or_defaults() -> configparser.ConfigParser:
    """設定を読めなくてもログだけは初期化できるよう、既定値のまま継続する。"""
    try:
        return load_config()
    except (OSError, configparser.Error):
        return configparser.ConfigParser()


def setup_logging(config: configparser.ConfigParser | None = None) -> None:
    if config is None:
        config = _load_config_or_defaults()

    try:
        log_directory = config.get('LOGGING', 'log_directory', fallback='logs')
        log_retention_days = config.getint('LOGGING', 'log_retention_days', fallback=7)
        project_name = config.get('LOGGING', 'project_name', fallback='KeepDrive')
        log_level = config.get('LOGGING', 'log_level', fallback='INFO')

        if not os.path.isabs(log_directory):
            project_root = os.path.dirname(os.path.dirname(__file__))
            log_directory = os.path.join(project_root, log_directory)

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        log_file = os.path.join(log_directory, f'{project_name}.log')

        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='midnight',
            backupCount=log_retention_days,
            encoding='utf-8'
        )
        file_handler.suffix = "%Y-%m-%d.log"

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        root_logger = logging.getLogger()

        try:
            level = getattr(logging, log_level.upper())
            root_logger.setLevel(level)
        except AttributeError:
            root_logger.setLevel(logging.INFO)
            logging.warning(f"無効なログレベル '{log_level}' が指定されました。INFOを使用します。")

        root_logger.addHandler(file_handler)

        # コマンドプロンプトで進行状況を追えるように、ファイルと同じレベルで簡潔に出力する
        # pythonw.exe 起動ではsys.stdoutがNoneになるため、コンソールがある場合だけ追加する
        if sys.stdout is not None:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S')
            )
            root_logger.addHandler(console_handler)

        cleanup_old_logs(log_directory, log_retention_days, project_name)

        logging.info(f"ログシステムが初期化されました: {log_file}")

    except PermissionError as e:
        raise PermissionError(f"ログディレクトリの作成権限がありません: {e}")
    except Exception as e:
        raise Exception(f"ログ設定の初期化中にエラーが発生しました: {e}")


def cleanup_old_logs(log_directory: str, retention_days: int, project_name: str) -> None:
    try:
        now = datetime.now()
        main_log_file = f'{project_name}.log'

        rotated_log_pattern = rf'{re.escape(project_name)}\.log\.\d{{4}}-\d{{2}}-\d{{2}}\.log$'

        deleted_count = 0
        for filename in os.listdir(log_directory):
            if filename.endswith('.log') and filename != main_log_file:
                if re.match(rotated_log_pattern, filename):
                    file_path = os.path.join(log_directory, filename)
                    try:
                        file_modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if now - file_modification_time >= timedelta(days=retention_days):
                            os.remove(file_path)
                            logging.info(f"古いログファイルを削除しました: {filename}")
                            deleted_count += 1
                    except OSError as e:
                        logging.error(f"ログファイルの削除中にエラーが発生しました {filename}: {str(e)}")

        if deleted_count > 0:
            logging.info(f"合計 {deleted_count} 個の古いログファイルを削除しました")

    except Exception as e:
        logging.error(f"ログクリーンアップ処理中にエラーが発生しました: {str(e)}")
