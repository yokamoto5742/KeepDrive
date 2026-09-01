from unittest.mock import MagicMock

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.constants import (
    KEEP_CARET_SETTLE_MS,
    KEEP_CLEAR_BODY_MAX_ATTEMPTS,
    KEEP_CLOSE_NOTE_LABEL,
    KEEP_COPY_TO_DOCS_LABEL,
    KEEP_LOGIN_URL_PREFIX,
    KEEP_MORE_MENU_LABEL,
    KEEP_NOTE_BODY_SELECTOR,
    KEEP_NOTE_CARD_SELECTOR,
    KEEP_OPEN_COPIED_DOC_LABEL,
)
from service.keep_browser import (
    clear_note_body,
    copy_note_to_google_docs,
    read_note_body,
)

COPIED_URL = 'https://docs.google.com/document/d/copied-1/edit'
KEEP_URL = 'https://keep.google.com/#search/text=memo'


def build_page(copied_url: str = COPIED_URL) -> MagicMock:
    page = MagicMock()
    page.url = KEEP_URL
    page.locator.return_value.filter.return_value.first = MagicMock()
    page.locator.return_value.inner_text.return_value = ''
    copied_page = MagicMock()
    copied_page.url = copied_url
    page.context.expect_page.return_value.__enter__.return_value.value = copied_page
    return page


def get_card(page: MagicMock) -> MagicMock:
    return page.locator.return_value.filter.return_value.first


def get_body(page: MagicMock) -> MagicMock:
    return page.locator.return_value


def get_copied_page(page: MagicMock) -> MagicMock:
    return page.context.expect_page.return_value.__enter__.return_value.value


def test_copy_note_opens_search_url_for_the_title() -> None:
    page = build_page()

    copy_note_to_google_docs(page, '人間関係')

    assert '%E4%BA%BA%E9%96%93%E9%96%A2%E4%BF%82' in page.goto.call_args.args[0]


def test_copy_note_reloads_when_already_on_keep() -> None:
    page = build_page()

    copy_note_to_google_docs(page, '人間関係')

    page.reload.assert_called_once()


def test_copy_note_does_not_reload_when_coming_from_another_page() -> None:
    page = build_page()
    page.url = COPIED_URL

    copy_note_to_google_docs(page, '人間関係')

    page.reload.assert_not_called()


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


def test_copy_note_raises_connection_error_when_redirected_to_login() -> None:
    page = build_page()
    page.url = f'{KEEP_LOGIN_URL_PREFIX}/ServiceLogin'

    with pytest.raises(ConnectionError):
        copy_note_to_google_docs(page, '人間関係')


def test_read_note_body_returns_the_body_text() -> None:
    page = build_page()
    get_body(page).inner_text.return_value = '本文'

    assert read_note_body(page, '人間関係') == '本文'
    assert page.locator.call_args_list[-1].args[0] == KEEP_NOTE_BODY_SELECTOR


def test_read_note_body_closes_the_note_without_editing_it() -> None:
    page = build_page()

    read_note_body(page, '人間関係')

    page.keyboard.press.assert_not_called()
    assert page.get_by_role.call_args_list[-1].kwargs['name'] == KEEP_CLOSE_NOTE_LABEL


def test_clear_note_body_selects_and_deletes_only_the_body() -> None:
    page = build_page()

    clear_note_body(page, '人間関係')

    get_card(page).click.assert_called_once()
    assert page.locator.call_args_list[-1].args[0] == KEEP_NOTE_BODY_SELECTOR
    get_body(page).click.assert_called()
    assert [call.args[0] for call in page.keyboard.press.call_args_list] == [
        'Control+A',
        'Delete',
    ]


def test_clear_note_body_closes_the_note_after_deleting() -> None:
    page = build_page()

    clear_note_body(page, '人間関係')

    assert page.get_by_role.call_args_list[-1].kwargs['name'] == KEEP_CLOSE_NOTE_LABEL


def test_clear_note_body_waits_before_selecting_all() -> None:
    page = build_page()

    clear_note_body(page, '人間関係')

    page.wait_for_timeout.assert_called_once_with(KEEP_CARET_SETTLE_MS)


def test_clear_note_body_retries_while_body_still_has_text() -> None:
    page = build_page()
    get_body(page).inner_text.side_effect = ['残った本文', '']

    clear_note_body(page, '人間関係')

    assert [call.args[0] for call in page.keyboard.press.call_args_list] == [
        'Control+A',
        'Delete',
        'Control+A',
        'Delete',
    ]


def test_clear_note_body_raises_when_body_still_has_text() -> None:
    page = build_page()
    get_body(page).inner_text.return_value = '残った本文'

    with pytest.raises(RuntimeError):
        clear_note_body(page, '人間関係')

    assert get_body(page).click.call_count == KEEP_CLEAR_BODY_MAX_ATTEMPTS


def test_clear_note_body_closes_the_note_even_when_it_fails() -> None:
    page = build_page()
    get_body(page).inner_text.return_value = '残った本文'

    with pytest.raises(RuntimeError):
        clear_note_body(page, '人間関係')

    # 開いたままだと次のメモの操作をオーバーレイが妨げる
    assert page.get_by_role.call_args_list[-1].kwargs['name'] == KEEP_CLOSE_NOTE_LABEL


def test_clear_note_body_raises_lookup_error_when_memo_is_missing() -> None:
    page = build_page()
    get_card(page).wait_for.side_effect = PlaywrightTimeoutError('timeout')

    with pytest.raises(LookupError):
        clear_note_body(page, '存在しないメモ')

    get_card(page).click.assert_not_called()
