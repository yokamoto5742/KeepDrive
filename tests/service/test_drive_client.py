from unittest.mock import MagicMock

from service.drive_client import (
    escape_query_value,
    find_document_ids_by_name,
    find_or_create_document,
    find_or_create_folder,
    trash_file,
)


def build_drive(found_files: list[dict], created_id: str = 'new-id') -> MagicMock:
    drive = MagicMock()
    drive.files().list().execute.return_value = {'files': found_files}
    drive.files().create().execute.return_value = {'id': created_id}
    return drive


def test_find_or_create_folder_reuses_existing() -> None:
    drive = build_drive([{'id': 'folder-1', 'name': '読書'}])
    drive.files().create.reset_mock()

    assert find_or_create_folder(drive, '読書') == 'folder-1'
    drive.files().create.assert_not_called()


def test_find_or_create_folder_creates_when_missing() -> None:
    drive = build_drive([], created_id='folder-2')

    assert find_or_create_folder(drive, '読書') == 'folder-2'

    body = drive.files().create.call_args.kwargs['body']
    assert body['name'] == '読書'
    assert body['parents'] == ['root']


def test_find_or_create_document_creates_inside_folder() -> None:
    drive = build_drive([], created_id='doc-1')

    assert find_or_create_document(drive, '読書', 'folder-1') == 'doc-1'

    body = drive.files().create.call_args.kwargs['body']
    assert body['parents'] == ['folder-1']
    assert body['mimeType'] == 'application/vnd.google-apps.document'


def test_find_or_create_document_query_targets_folder() -> None:
    drive = build_drive([{'id': 'doc-9', 'name': '読書'}])
    drive.files().list.reset_mock()

    find_or_create_document(drive, '読書', 'folder-1')

    query = drive.files().list.call_args.kwargs['q']
    assert "'folder-1' in parents" in query
    assert 'trashed=false' in query


def test_escape_query_value_escapes_quote_and_backslash() -> None:
    assert escape_query_value("It's") == "It\\'s"
    assert escape_query_value('a\\b') == 'a\\\\b'


def test_find_or_create_folder_escapes_name_in_query() -> None:
    drive = build_drive([{'id': 'folder-1', 'name': "It's"}])
    drive.files().list.reset_mock()

    find_or_create_folder(drive, "It's")

    assert "name='It\\'s'" in drive.files().list.call_args.kwargs['q']


def test_find_document_ids_by_name_returns_ids_in_created_order() -> None:
    drive = build_drive([{'id': 'doc-1'}, {'id': 'doc-2'}])
    drive.files().list.reset_mock()

    assert find_document_ids_by_name(drive, '人間関係') == ['doc-1', 'doc-2']
    assert drive.files().list.call_args.kwargs['orderBy'] == 'createdTime'


def test_find_document_ids_by_name_returns_empty_when_missing() -> None:
    drive = build_drive([])

    assert find_document_ids_by_name(drive, '人間関係') == []


def test_find_document_ids_by_name_searches_whole_drive() -> None:
    drive = build_drive([])
    drive.files().list.reset_mock()

    find_document_ids_by_name(drive, '人間関係')

    assert 'in parents' not in drive.files().list.call_args.kwargs['q']


def test_trash_file_marks_trashed_instead_of_deleting() -> None:
    drive = MagicMock()

    trash_file(drive, 'doc-9')

    drive.files().update.assert_called_once_with(
        fileId='doc-9', body={'trashed': True}
    )
    drive.files().delete.assert_not_called()
