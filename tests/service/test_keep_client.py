from unittest.mock import MagicMock

from gkeepapi.node import List as KeepList
from gkeepapi.node import Note

from service.keep_client import clear_list_items, fetch_list_notes


def make_keep_list(
    title: str,
    item_count: int = 1,
    trashed: bool = False,
    archived: bool = False,
) -> MagicMock:
    """isinstance判定を通すためspec付きのモックを使う。"""
    note = MagicMock(spec=KeepList)
    note.title = title
    note.items = [MagicMock() for _ in range(item_count)]
    note.trashed = trashed
    note.archived = archived
    return note


def build_keep(nodes: list) -> MagicMock:
    keep = MagicMock()
    keep.all.return_value = nodes
    return keep


def test_fetch_list_notes_returns_valid_lists() -> None:
    valid = make_keep_list('読書')

    assert fetch_list_notes(build_keep([valid])) == [valid]


def test_fetch_list_notes_excludes_untitled() -> None:
    assert fetch_list_notes(build_keep([make_keep_list('')])) == []


def test_fetch_list_notes_excludes_empty_list() -> None:
    assert fetch_list_notes(build_keep([make_keep_list('読書', item_count=0)])) == []


def test_fetch_list_notes_excludes_trashed_and_archived() -> None:
    nodes = [
        make_keep_list('ゴミ箱', trashed=True),
        make_keep_list('アーカイブ', archived=True),
    ]

    assert fetch_list_notes(build_keep(nodes)) == []


def test_fetch_list_notes_excludes_plain_notes() -> None:
    plain = MagicMock(spec=Note)
    plain.title = 'メモ'

    assert fetch_list_notes(build_keep([plain])) == []


def test_clear_list_items_deletes_every_item() -> None:
    note = make_keep_list('読書', item_count=3)

    clear_list_items(note)

    for item in note.items:
        item.delete.assert_called_once_with()
