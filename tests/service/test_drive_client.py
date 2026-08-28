from unittest.mock import MagicMock

from service.drive_client import (
    escape_query_value,
    find_document_ids_by_name,
    trash_file,
)


def build_drive(found_files: list[dict]) -> MagicMock:
    drive = MagicMock()
    drive.files().list().execute.return_value = {'files': found_files}
    drive.files().list.reset_mock()
    return drive


def test_find_document_ids_by_name_returns_ids_in_created_order() -> None:
    drive = build_drive([{'id': 'doc-1'}, {'id': 'doc-2'}])

    assert find_document_ids_by_name(drive, '人間関係') == ['doc-1', 'doc-2']
    assert drive.files().list.call_args.kwargs['orderBy'] == 'createdTime'


def test_find_document_ids_by_name_returns_empty_when_missing() -> None:
    drive = build_drive([])

    assert find_document_ids_by_name(drive, '人間関係') == []


def test_find_document_ids_by_name_searches_whole_drive() -> None:
    drive = build_drive([])

    find_document_ids_by_name(drive, '人間関係')

    query = drive.files().list.call_args.kwargs['q']
    assert 'in parents' not in query
    assert 'trashed=false' in query


def test_find_document_ids_by_name_escapes_name_in_query() -> None:
    drive = build_drive([])

    find_document_ids_by_name(drive, "It's")

    assert "name='It\\'s'" in drive.files().list.call_args.kwargs['q']


def test_trash_file_marks_trashed_instead_of_deleting() -> None:
    drive = MagicMock()

    trash_file(drive, 'doc-9')

    drive.files().update.assert_called_once_with(
        fileId='doc-9', body={'trashed': True}
    )
    drive.files().delete.assert_not_called()


def test_escape_query_value_escapes_backslash_and_quote() -> None:
    assert escape_query_value("a\\b") == "a\\\\b"
    assert escape_query_value("It's") == "It\\'s"
