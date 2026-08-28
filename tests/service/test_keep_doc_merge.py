from typing import Any
from unittest.mock import MagicMock

import pytest

from service.keep_doc_merge import merge_memo


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('service.keep_doc_merge.time.sleep', lambda _: None)


@pytest.fixture
def stubs(monkeypatch: pytest.MonkeyPatch) -> dict[str, MagicMock]:
    """merge_memo が呼び出す下位関数をすべて差し替える。"""
    stub_names = (
        'find_document_ids_by_name',
        'copy_note_to_google_docs',
        'extract_text',
        'append_text',
        'trash_file',
    )
    created = {name: MagicMock() for name in stub_names}
    for name, stub in created.items():
        monkeypatch.setattr(f'service.keep_doc_merge.{name}', stub)
    created['extract_text'].return_value = '本文\n'
    return created


def set_found_ids(stubs: dict[str, MagicMock], *responses: list[str]) -> None:
    stubs['find_document_ids_by_name'].side_effect = list(responses)


def call_merge(docs: Any = None) -> None:
    merge_memo(MagicMock(), MagicMock(), docs or MagicMock(), '人間関係')


def test_merge_memo_appends_copy_to_existing_document(
    stubs: dict[str, MagicMock]
) -> None:
    set_found_ids(stubs, ['existing-1'], ['existing-1', 'copied-1'])
    docs = MagicMock()

    call_merge(docs)

    stubs['append_text'].assert_called_once_with(docs, 'existing-1', '本文\n')
    stubs['extract_text'].assert_called_once_with(docs, 'copied-1')


def test_merge_memo_trashes_copy_after_merge(stubs: dict[str, MagicMock]) -> None:
    set_found_ids(stubs, ['existing-1'], ['existing-1', 'copied-1'])

    call_merge()

    assert stubs['trash_file'].call_args.args[1] == 'copied-1'


def test_merge_memo_keeps_copy_when_no_existing_document(
    stubs: dict[str, MagicMock]
) -> None:
    set_found_ids(stubs, [], ['copied-1'])

    call_merge()

    stubs['append_text'].assert_not_called()
    stubs['trash_file'].assert_not_called()


def test_merge_memo_uses_oldest_existing_document(
    stubs: dict[str, MagicMock]
) -> None:
    set_found_ids(
        stubs, ['existing-1', 'existing-2'], ['existing-1', 'existing-2', 'copied-1']
    )

    call_merge()

    assert stubs['append_text'].call_args.args[1] == 'existing-1'


def test_merge_memo_waits_until_copy_appears_in_drive(
    stubs: dict[str, MagicMock]
) -> None:
    set_found_ids(
        stubs, ['existing-1'], ['existing-1'], ['existing-1', 'copied-1']
    )

    call_merge()

    assert stubs['find_document_ids_by_name'].call_count == 3
    assert stubs['trash_file'].call_args.args[1] == 'copied-1'


def test_merge_memo_raises_when_copy_never_appears(
    stubs: dict[str, MagicMock]
) -> None:
    stubs['find_document_ids_by_name'].return_value = ['existing-1']

    with pytest.raises(LookupError):
        call_merge()

    stubs['append_text'].assert_not_called()


def test_merge_memo_normalizes_trailing_newlines(
    stubs: dict[str, MagicMock]
) -> None:
    set_found_ids(stubs, ['existing-1'], ['existing-1', 'copied-1'])
    stubs['extract_text'].return_value = '本文\n\n\n'

    call_merge()

    assert stubs['append_text'].call_args.args[2] == '本文\n'


def test_merge_memo_copies_before_searching_for_the_new_document(
    stubs: dict[str, MagicMock]
) -> None:
    set_found_ids(stubs, ['existing-1'], ['existing-1', 'copied-1'])

    call_merge()

    assert stubs['copy_note_to_google_docs'].call_args.args[1] == '人間関係'
