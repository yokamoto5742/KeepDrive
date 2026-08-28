from unittest.mock import MagicMock, call

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.constants import DOCS_FILE_MENU_LABEL, DOCS_MOVE_TO_TRASH_LABEL
from service.docs_browser import (
    append_text,
    extract_document_id,
    fetch_document_text,
    move_to_trash,
)

DOCUMENT_URL = 'https://docs.google.com/document/d/doc-1/edit'


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('service.docs_browser.time.sleep', lambda _: None)


def build_export_response(text: str) -> MagicMock:
    response = MagicMock(ok=True, status=200)
    response.text.return_value = text
    return response


def build_page(*export_texts: str) -> MagicMock:
    """エクスポート結果を呼び出し順に返すページを作る。"""
    page = MagicMock()
    page.request.get.side_effect = [
        build_export_response(text) for text in export_texts
    ]
    return page


def test_extract_document_id_from_url() -> None:
    assert extract_document_id(DOCUMENT_URL) == 'doc-1'


def test_extract_document_id_rejects_other_url() -> None:
    with pytest.raises(ValueError):
        extract_document_id('https://keep.google.com/#search/text=memo')


def test_fetch_document_text_requests_text_export() -> None:
    page = build_page('本文\r\n')

    assert fetch_document_text(page, DOCUMENT_URL) == '本文\n'
    assert page.request.get.call_args.args[0] == (
        'https://docs.google.com/document/d/doc-1/export?format=txt'
    )


def test_fetch_document_text_raises_when_response_is_not_ok() -> None:
    page = MagicMock()
    page.request.get.return_value = MagicMock(ok=False, status=403)

    with pytest.raises(RuntimeError):
        fetch_document_text(page, DOCUMENT_URL)


def test_append_text_inputs_paragraphs_at_the_end_of_the_document() -> None:
    page = build_page('既存\n', '既存\n\n追記1\n追記2\n')

    append_text(page, DOCUMENT_URL, '\n追記1\n追記2')

    page.keyboard.press.assert_any_call('Control+End')
    assert page.keyboard.insert_text.call_args_list == [call('追記1'), call('追記2')]


def test_append_text_raises_when_change_is_not_saved() -> None:
    page = build_page(*['既存\n'] * 20)

    with pytest.raises(TimeoutError):
        append_text(page, DOCUMENT_URL, '\n追記1')


def test_move_to_trash_uses_file_menu() -> None:
    page = MagicMock()

    move_to_trash(page, DOCUMENT_URL)

    assert page.goto.call_args.args[0] == DOCUMENT_URL
    assert [call_args.kwargs['name'] for call_args in page.get_by_role.call_args_list] == [
        DOCS_FILE_MENU_LABEL,
        DOCS_MOVE_TO_TRASH_LABEL,
        DOCS_MOVE_TO_TRASH_LABEL,
    ]


def test_move_to_trash_ignores_missing_confirm_dialog() -> None:
    page = MagicMock()
    page.get_by_role.return_value.click.side_effect = [
        None,
        None,
        PlaywrightTimeoutError('timeout'),
    ]

    move_to_trash(page, DOCUMENT_URL)
