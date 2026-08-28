from unittest.mock import MagicMock

import pytest

from service.keep_doc_merge import merge_memo

COPIED_URL = 'https://docs.google.com/document/d/copied-1/edit'
DESTINATION_URL = 'https://docs.google.com/document/d/existing-1/edit'


@pytest.fixture
def stubs(monkeypatch: pytest.MonkeyPatch) -> dict[str, MagicMock]:
    """merge_memo が呼び出す下位関数をすべて差し替える。"""
    stub_names = (
        'copy_note_to_google_docs',
        'fetch_document_text',
        'append_text',
        'move_to_trash',
    )
    created = {name: MagicMock() for name in stub_names}
    for name, stub in created.items():
        monkeypatch.setattr(f'service.keep_doc_merge.{name}', stub)
    created['copy_note_to_google_docs'].return_value = COPIED_URL
    created['fetch_document_text'].return_value = '本文\n'
    return created


def call_merge(page: MagicMock | None = None) -> None:
    merge_memo(page or MagicMock(), '人間関係', DESTINATION_URL)


def test_merge_memo_appends_copied_text_to_destination(
    stubs: dict[str, MagicMock]
) -> None:
    call_merge()

    assert stubs['copy_note_to_google_docs'].call_args.args[1] == '人間関係'
    assert stubs['fetch_document_text'].call_args.args[1] == COPIED_URL
    assert stubs['append_text'].call_args.args[1:] == (DESTINATION_URL, '\n本文')


def test_merge_memo_trashes_copy_after_merge(stubs: dict[str, MagicMock]) -> None:
    call_merge()

    assert stubs['move_to_trash'].call_args.args[1] == COPIED_URL


def test_merge_memo_keeps_copy_when_append_fails(
    stubs: dict[str, MagicMock]
) -> None:
    stubs['append_text'].side_effect = TimeoutError('未保存')

    with pytest.raises(TimeoutError):
        call_merge()

    stubs['move_to_trash'].assert_not_called()


def test_merge_memo_normalizes_surrounding_newlines(
    stubs: dict[str, MagicMock]
) -> None:
    stubs['fetch_document_text'].return_value = '\n本文\n\n\n'

    call_merge()

    assert stubs['append_text'].call_args.args[2] == '\n本文'
