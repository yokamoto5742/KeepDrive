from contextlib import contextmanager
from typing import Iterator
from unittest.mock import MagicMock

import pytest

import main


@pytest.fixture
def stubs(monkeypatch: pytest.MonkeyPatch) -> dict[str, MagicMock]:
    """run() が呼び出す下位関数を差し替える。"""
    created = {
        name: MagicMock()
        for name in (
            'load_config',
            'setup_logging',
            'get_target_memo_titles',
            'load_credentials',
            'build_drive_service',
            'build_docs_service',
            'merge_memo',
        )
    }
    for name, stub in created.items():
        monkeypatch.setattr(f'main.{name}', stub)

    @contextmanager
    def fake_page() -> Iterator[MagicMock]:
        yield MagicMock()

    monkeypatch.setattr('main.open_keep_page', fake_page)
    created['get_target_memo_titles'].return_value = ['人間関係']
    return created


def test_run_returns_zero_when_all_memos_succeed(
    stubs: dict[str, MagicMock]
) -> None:
    stubs['get_target_memo_titles'].return_value = ['人間関係', '読書']

    assert main.run() == 0
    assert stubs['merge_memo'].call_count == 2


def test_run_returns_one_without_target_memo(stubs: dict[str, MagicMock]) -> None:
    stubs['get_target_memo_titles'].return_value = []

    assert main.run() == 1
    stubs['load_credentials'].assert_not_called()


def test_run_continues_after_a_failed_memo(stubs: dict[str, MagicMock]) -> None:
    stubs['get_target_memo_titles'].return_value = ['人間関係', '読書']
    stubs['merge_memo'].side_effect = [RuntimeError('コピー失敗'), None]

    assert main.run() == 1
    assert stubs['merge_memo'].call_count == 2


def test_main_returns_one_on_unexpected_error(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr('main.run', MagicMock(side_effect=RuntimeError('想定外')))

    assert main.main() == 1
