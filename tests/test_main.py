from contextlib import contextmanager
from typing import Iterator
from unittest.mock import MagicMock

import pytest

import main

DOCUMENT_URL = 'https://docs.google.com/document/d/doc-1/edit'


@pytest.fixture
def stubs(monkeypatch: pytest.MonkeyPatch) -> dict[str, MagicMock]:
    """run() が呼び出す下位関数を差し替える。"""
    created = {
        name: MagicMock()
        for name in (
            'load_config',
            'setup_logging',
            'get_merge_targets',
            'merge_memo',
        )
    }
    for name, stub in created.items():
        monkeypatch.setattr(f'main.{name}', stub)

    opened_page = MagicMock()

    @contextmanager
    def fake_page() -> Iterator[MagicMock]:
        yield opened_page

    monkeypatch.setattr('main.open_chrome_page', fake_page)
    created['get_merge_targets'].return_value = {'人間関係': DOCUMENT_URL}
    return created


def test_run_returns_zero_when_all_memos_succeed(
    stubs: dict[str, MagicMock]
) -> None:
    stubs['get_merge_targets'].return_value = {
        '人間関係': DOCUMENT_URL,
        '読書': DOCUMENT_URL,
    }

    assert main.run() == 0
    assert stubs['merge_memo'].call_count == 2


def test_run_passes_title_and_destination_url_to_merge(
    stubs: dict[str, MagicMock]
) -> None:
    assert main.run() == 0
    assert stubs['merge_memo'].call_args.args[1:] == ('人間関係', DOCUMENT_URL)


def test_run_returns_one_without_target_memo(stubs: dict[str, MagicMock]) -> None:
    stubs['get_merge_targets'].return_value = {}

    assert main.run() == 1
    stubs['merge_memo'].assert_not_called()


def test_run_continues_after_a_failed_memo(stubs: dict[str, MagicMock]) -> None:
    stubs['get_merge_targets'].return_value = {
        '人間関係': DOCUMENT_URL,
        '読書': DOCUMENT_URL,
    }
    stubs['merge_memo'].side_effect = [RuntimeError('コピー失敗'), None]

    assert main.run() == 1
    assert stubs['merge_memo'].call_count == 2


def test_main_returns_one_on_unexpected_error(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr('main.run', MagicMock(side_effect=RuntimeError('想定外')))

    assert main.main() == 1
