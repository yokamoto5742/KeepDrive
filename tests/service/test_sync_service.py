import datetime
from unittest.mock import MagicMock

from tests.conftest import make_item, make_note
from service.sync_service import (
    build_append_text,
    filter_target_notes,
    sort_items,
    sync_notes,
)


def test_sort_items_orders_by_updated_desc(base_time: datetime.datetime) -> None:
    old = make_item('あ', base_time - datetime.timedelta(hours=1))
    new = make_item('ん', base_time)

    assert sort_items([old, new]) == [new, old]


def test_sort_items_uses_text_asc_for_same_timestamp(
    base_time: datetime.datetime,
) -> None:
    banana = make_item('banana', base_time)
    apple = make_item('apple', base_time)

    assert sort_items([banana, apple]) == [apple, banana]


def test_build_append_text_contains_item_names_only(
    base_time: datetime.datetime,
) -> None:
    items = [
        make_item('牛乳', base_time),
        make_item('卵', base_time - datetime.timedelta(minutes=1)),
    ]

    assert build_append_text(items) == '牛乳\n卵\n'


def test_filter_target_notes_returns_all_when_unspecified() -> None:
    notes = [make_note('読書'), make_note('生活')]

    assert filter_target_notes(notes, []) == notes


def test_filter_target_notes_selects_specified_names() -> None:
    reading = make_note('読書')
    notes = [reading, make_note('生活')]

    assert filter_target_notes(notes, ['読書']) == [reading]


def test_filter_target_notes_warns_for_missing_names(caplog) -> None:
    with caplog.at_level('WARNING'):
        result = filter_target_notes([make_note('読書')], ['読書', '存在しない'])

    assert len(result) == 1
    assert '存在しない' in caplog.text


def test_sync_notes_clears_items_after_successful_append(
    base_time: datetime.datetime, mocker
) -> None:
    note = make_note('読書', [make_item('本A', base_time)])
    mocker.patch('service.sync_service.find_or_create_folder', return_value='f1')
    mocker.patch('service.sync_service.find_or_create_document', return_value='d1')
    mocker.patch('service.sync_service.append_text')
    clear = mocker.patch('service.sync_service.clear_list_items')

    result = sync_notes([note], MagicMock(), MagicMock())

    clear.assert_called_once_with(note)
    assert result.success_count == 1
    assert result.failure_count == 0


def test_sync_notes_keeps_items_when_append_fails(
    base_time: datetime.datetime, mocker
) -> None:
    note = make_note('読書', [make_item('本A', base_time)])
    mocker.patch('service.sync_service.find_or_create_folder', return_value='f1')
    mocker.patch('service.sync_service.find_or_create_document', return_value='d1')
    mocker.patch('service.sync_service.append_text', side_effect=RuntimeError('API失敗'))
    clear = mocker.patch('service.sync_service.clear_list_items')

    result = sync_notes([note], MagicMock(), MagicMock())

    clear.assert_not_called()
    assert result.success_count == 0
    assert result.failure_count == 1


def test_sync_notes_continues_after_one_failure(
    base_time: datetime.datetime, mocker
) -> None:
    failing = make_note('読書', [make_item('本A', base_time)])
    passing = make_note('生活', [make_item('掃除', base_time)])
    mocker.patch('service.sync_service.find_or_create_folder', return_value='f1')
    mocker.patch(
        'service.sync_service.find_or_create_document',
        side_effect=[RuntimeError('API失敗'), 'd2'],
    )
    mocker.patch('service.sync_service.append_text')
    clear = mocker.patch('service.sync_service.clear_list_items')

    result = sync_notes([failing, passing], MagicMock(), MagicMock())

    clear.assert_called_once_with(passing)
    assert result == (1, 1)
