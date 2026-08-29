from unittest.mock import MagicMock

import pytest

from service.keep_doc_merge import _remove_duplicate_lines, merge_memo

COPIED_URL = 'https://docs.google.com/document/d/copied-1/edit'
DESTINATION_URL = 'https://docs.google.com/document/d/existing-1/edit'


@pytest.fixture
def stubs(monkeypatch: pytest.MonkeyPatch) -> dict[str, MagicMock]:
    """merge_memo が呼び出す下位関数をすべて差し替える。"""
    stub_names = (
        'read_note_body',
        'copy_note_to_google_docs',
        'fetch_document_text',
        'append_text',
        'move_to_trash',
        'clear_note_body',
    )
    created = {name: MagicMock() for name in stub_names}
    for name, stub in created.items():
        monkeypatch.setattr(f'service.keep_doc_merge.{name}', stub)
    created['read_note_body'].return_value = '本文'
    created['copy_note_to_google_docs'].return_value = COPIED_URL
    set_documents(created, copied='本文\n', destination='既存\n')
    return created


def set_documents(stubs: dict[str, MagicMock], copied: str, destination: str) -> None:
    """コピー先と結合先で異なる本文を返すようにする。"""
    texts = {COPIED_URL: copied, DESTINATION_URL: destination}
    stubs['fetch_document_text'].side_effect = lambda _page, url: texts[url]


def call_merge(page: MagicMock | None = None) -> None:
    merge_memo(page or MagicMock(), '人間関係', DESTINATION_URL)


def test_merge_memo_appends_copied_text_to_destination(
    stubs: dict[str, MagicMock]
) -> None:
    call_merge()

    assert stubs['copy_note_to_google_docs'].call_args.args[1] == '人間関係'
    assert stubs['append_text'].call_args.args[1:] == (DESTINATION_URL, '\n本文')


def test_merge_memo_trashes_copy_after_merge(stubs: dict[str, MagicMock]) -> None:
    call_merge()

    assert stubs['move_to_trash'].call_args.args[1] == COPIED_URL


def test_merge_memo_clears_note_body_after_trashing_copy(
    stubs: dict[str, MagicMock]
) -> None:
    call_merge()

    assert stubs['clear_note_body'].call_args.args[1] == '人間関係'


def test_merge_memo_keeps_copy_when_append_fails(
    stubs: dict[str, MagicMock]
) -> None:
    stubs['append_text'].side_effect = TimeoutError('未保存')

    with pytest.raises(TimeoutError):
        call_merge()

    stubs['move_to_trash'].assert_not_called()
    stubs['clear_note_body'].assert_not_called()


def test_merge_memo_normalizes_surrounding_newlines(
    stubs: dict[str, MagicMock]
) -> None:
    set_documents(stubs, copied='\n本文\n\n\n', destination='既存')

    call_merge()

    assert stubs['append_text'].call_args.args[2] == '\n本文'


def test_merge_memo_appends_only_lines_missing_from_destination(
    stubs: dict[str, MagicMock]
) -> None:
    set_documents(stubs, copied='人間関係\n既存の行\n新しい行\n', destination='既存の行\n')

    call_merge()

    assert stubs['append_text'].call_args.args[2] == '\n人間関係\n新しい行'


def test_merge_memo_skips_append_when_everything_is_duplicated(
    stubs: dict[str, MagicMock]
) -> None:
    set_documents(stubs, copied='既存の行\n', destination='既存の行\n')

    call_merge()

    stubs['append_text'].assert_not_called()
    # 全内容が結合先にある状態なので、コピー削除とメモ本文削除は実行する
    stubs['move_to_trash'].assert_called_once()
    stubs['clear_note_body'].assert_called_once()


def test_merge_memo_skips_everything_when_note_body_is_empty(
    stubs: dict[str, MagicMock]
) -> None:
    stubs['read_note_body'].return_value = '  \n '

    call_merge()

    stubs['copy_note_to_google_docs'].assert_not_called()
    stubs['append_text'].assert_not_called()
    stubs['move_to_trash'].assert_not_called()
    stubs['clear_note_body'].assert_not_called()


def test_merge_memo_appends_without_leading_blank_line_to_empty_destination(
    stubs: dict[str, MagicMock]
) -> None:
    set_documents(stubs, copied='本文\n', destination='\n')

    call_merge()

    assert stubs['append_text'].call_args.args[2] == '本文'


def test_remove_duplicate_lines_drops_lines_already_in_destination() -> None:
    assert _remove_duplicate_lines('a\nb\nc', 'b') == 'a\nc'


def test_remove_duplicate_lines_drops_repeats_inside_the_copy() -> None:
    assert _remove_duplicate_lines('a\nb\na', '') == 'a\nb'


def test_remove_duplicate_lines_ignores_surrounding_spaces() -> None:
    assert _remove_duplicate_lines('  a  \nb', 'a') == 'b'


def test_remove_duplicate_lines_keeps_blank_lines_as_paragraph_breaks() -> None:
    assert _remove_duplicate_lines('a\n\nb', '') == 'a\n\nb'


def test_remove_duplicate_lines_returns_empty_when_all_lines_are_duplicated() -> None:
    assert _remove_duplicate_lines('a\n\nb\n', 'a\nb') == ''
