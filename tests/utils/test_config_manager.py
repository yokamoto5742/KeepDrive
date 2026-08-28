import configparser

import pytest

from utils.config_manager import get_target_list_names, get_target_memo_titles


def build_config(
    raw_value: str | None, key: str = 'target_lists'
) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if raw_value is not None:
        config['KEEP'] = {key: raw_value}
    return config


@pytest.mark.parametrize(
    ('raw_value', 'expected'),
    [
        ('', []),
        ('読書', ['読書']),
        ('読書,ショッピング,生活', ['読書', 'ショッピング', '生活']),
        (' 読書 , ショッピング ', ['読書', 'ショッピング']),
        ('読書,,ショッピング,', ['読書', 'ショッピング']),
    ],
)
def test_get_target_list_names(raw_value: str, expected: list[str]) -> None:
    assert get_target_list_names(build_config(raw_value)) == expected


def test_get_target_list_names_without_section() -> None:
    assert get_target_list_names(build_config(None)) == []


@pytest.mark.parametrize(
    ('raw_value', 'expected'),
    [
        ('', []),
        ('人間関係', ['人間関係']),
        ('人間関係, 読書 ,', ['人間関係', '読書']),
    ],
)
def test_get_target_memo_titles(raw_value: str, expected: list[str]) -> None:
    assert get_target_memo_titles(build_config(raw_value, 'target_memo')) == expected


def test_get_target_memo_titles_without_section() -> None:
    assert get_target_memo_titles(build_config(None)) == []
