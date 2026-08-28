import configparser

import pytest

from utils.config_manager import CaseSensitiveConfigParser, get_merge_targets

DOCUMENT_URL = 'https://docs.google.com/document/d/doc-1/edit'


def build_config(values: dict[str, str] | None) -> configparser.ConfigParser:
    config = CaseSensitiveConfigParser()
    if values is not None:
        config['KEEP'] = values
    return config


def test_get_merge_targets_returns_title_and_url_pairs() -> None:
    config = build_config({'人間関係': DOCUMENT_URL, '読書': f' {DOCUMENT_URL} '})

    assert get_merge_targets(config) == {
        '人間関係': DOCUMENT_URL,
        '読書': DOCUMENT_URL,
    }


def test_get_merge_targets_skips_entries_without_url() -> None:
    config = build_config({'人間関係': DOCUMENT_URL, '読書': ''})

    assert get_merge_targets(config) == {'人間関係': DOCUMENT_URL}


def test_get_merge_targets_keeps_key_case() -> None:
    config = build_config({'Books': DOCUMENT_URL})

    assert get_merge_targets(config) == {'Books': DOCUMENT_URL}


def test_get_merge_targets_without_section() -> None:
    assert get_merge_targets(build_config(None)) == {}


@pytest.mark.parametrize('title', ['人間関係', 'Books'])
def test_case_sensitive_parser_reads_ini_keys_as_written(title: str) -> None:
    config = CaseSensitiveConfigParser()
    config.read_string(f'[KEEP]\n{title} = {DOCUMENT_URL}\n')

    assert get_merge_targets(config) == {title: DOCUMENT_URL}
