import configparser

import pytest

from utils.config_manager import get_target_memo_titles


def build_config(raw_value: str | None) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if raw_value is not None:
        config['KEEP'] = {'target_memo': raw_value}
    return config


@pytest.mark.parametrize(
    ('raw_value', 'expected'),
    [
        ('', []),
        ('人間関係', ['人間関係']),
        ('人間関係,読書,生活', ['人間関係', '読書', '生活']),
        (' 人間関係 , 読書 ', ['人間関係', '読書']),
        ('人間関係,,読書,', ['人間関係', '読書']),
    ],
)
def test_get_target_memo_titles(raw_value: str, expected: list[str]) -> None:
    assert get_target_memo_titles(build_config(raw_value)) == expected


def test_get_target_memo_titles_without_section() -> None:
    assert get_target_memo_titles(build_config(None)) == []
