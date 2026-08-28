from unittest.mock import MagicMock

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.constants import KEEP_COPY_TO_DOCS_LABEL, KEEP_MORE_MENU_LABEL
from service.keep_browser import copy_note_to_google_docs


def build_page() -> MagicMock:
    page = MagicMock()
    page.get_by_role.return_value.filter.return_value.first = MagicMock()
    return page


def get_card(page: MagicMock) -> MagicMock:
    return page.get_by_role.return_value.filter.return_value.first


def test_copy_note_opens_search_url_for_the_title() -> None:
    page = build_page()

    copy_note_to_google_docs(page, '人間関係')

    assert '%E4%BA%BA%E9%96%93%E9%96%A2%E4%BF%82' in page.goto.call_args.args[0]


def test_copy_note_clicks_copy_to_docs_menu_item() -> None:
    page = build_page()

    copy_note_to_google_docs(page, '人間関係')

    get_card(page).hover.assert_called_once()
    assert (
        get_card(page).get_by_role.call_args.kwargs['name'] == KEEP_MORE_MENU_LABEL
    )
    assert page.get_by_role.call_args.kwargs['name'] == KEEP_COPY_TO_DOCS_LABEL
    page.get_by_role.return_value.click.assert_called_once()


def test_copy_note_raises_lookup_error_when_memo_is_missing() -> None:
    page = build_page()
    get_card(page).wait_for.side_effect = PlaywrightTimeoutError('timeout')

    with pytest.raises(LookupError):
        copy_note_to_google_docs(page, '存在しないメモ')

    get_card(page).hover.assert_not_called()
