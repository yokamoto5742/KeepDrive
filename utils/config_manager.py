import configparser
from pathlib import Path
from typing import Final

from app.constants import CONFIG_SECTION_KEEP, MSG_CONFIG_NOT_FOUND

CONFIG_PATH: Final[Path] = Path(__file__).resolve().parent / 'config.ini'


class CaseSensitiveConfigParser(configparser.ConfigParser):
    """メモタイトルをキーに使うため、キーの大文字小文字をそのまま保持する。"""

    def optionxform(self, optionstr: str) -> str:
        return optionstr


def load_config(config_file: Path = CONFIG_PATH) -> configparser.ConfigParser:
    if not config_file.exists():
        raise FileNotFoundError(MSG_CONFIG_NOT_FOUND.format(path=config_file))

    config = CaseSensitiveConfigParser()
    config.read(config_file, encoding='utf-8')
    return config


def get_merge_targets(config: configparser.ConfigParser) -> dict[str, str]:
    """メモタイトルと結合先ドキュメントURLの対応を取得する。"""
    if not config.has_section(CONFIG_SECTION_KEEP):
        return {}

    return {
        title: url.strip()
        for title, url in config.items(CONFIG_SECTION_KEEP)
        if url.strip()
    }
