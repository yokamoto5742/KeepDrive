from unittest.mock import MagicMock

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.constants import (
    KEEP_COPY_TO_DOCS_LABEL,
    KEEP_MORE_MENU_LABEL,
    KEEP_NOTE_CARD_SELECTOR,
    KEEP_OPEN_COPIED_DOC_LABEL,
)
from service.keep_browser import copy_note_to_google_docs

COPIED_URL = 'https://docs.google.com/document/d/copied-1/edit'


def build_page(copied_url: str = COPIED_URL) -> MagicMock:
    page = MagicMock()
    page.locator.return_value.filter.return_value.first = MagicMock()
    copied_page = MagicMock()
    copied_page.url = copied_url
    page.context.expect_page.return_value.__enter__.return_value.value = copied_page
    return page


def get_card(page: MagicMock) -> MagicMock:
    return page.locator.return_value.filter.return_value.first


def get_copied_page(page: MagicMock) -> MagicMock:
    return page.context.expect_page.return_value.__enter__.return_value.value


def test_copy_note_opens_search_url_for_the_title() -> None:
    page = build_page()

    copy_note_to_google_docs(page, '人間関係')

    assert '%E4%BA%BA%E9%96%93%E9%96%A2%E4%BF%82' in page.goto.call_args.args[0]


def test_copy_note_finds_card_by_note_card_selector() -> None:
    page = build_page()

    copy_note_to_google_docs(page, '人間関係')

    page.locator.assert_called_once_with(KEEP_NOTE_CARD_SELECTOR)


def test_copy_note_clicks_copy_to_docs_menu_item() -> None:
    page = build_page()

    copy_note_to_google_docs(page, '人間関係')

    get_card(page).hover.assert_called_once()
    assert (
        get_card(page).get_by_role.call_args.kwargs['name'] == KEEP_MORE_MENU_LABEL
    )
    assert [
        call.kwargs['name']
        for call in page.get_by_role.call_args_list
        if 'name' in call.kwargs
    ] == [KEEP_COPY_TO_DOCS_LABEL, KEEP_OPEN_COPIED_DOC_LABEL]


def test_copy_note_returns_copied_document_url() -> None:
    page = build_page()

    assert copy_note_to_google_docs(page, '人間関係') == COPIED_URL
    get_copied_page(page).close.assert_called_once()


def test_copy_note_raises_lookup_error_when_memo_is_missing() -> None:
    page = build_page()
    get_card(page).wait_for.side_effect = PlaywrightTimeoutError('timeout')

    with pytest.raises(LookupError):
        copy_note_to_google_docs(page, '存在しないメモ')

    get_card(page).hover.assert_not_called()


def test_copy_note_raises_lookup_error_when_copied_document_does_not_open() -> None:
    page = build_page()
    page.context.expect_page.return_value.__enter__.side_effect = (
        PlaywrightTimeoutError('timeout')
    )

    with pytest.raises(LookupError):
        copy_note_to_google_docs(page, '人間関係')
