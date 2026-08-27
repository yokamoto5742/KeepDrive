import datetime
from typing import cast
from unittest.mock import MagicMock

import pytest
from gkeepapi.node import List as KeepList
from gkeepapi.node import ListItem


def make_item(text: str, updated: datetime.datetime) -> ListItem:
    """ListItemの代替スタブ。textとtimestamps.updatedのみ使用する。"""
    item = MagicMock()
    item.text = text
    item.timestamps.updated = updated
    return cast(ListItem, item)


def make_note(
    title: str,
    items: list[ListItem] | None = None,
    trashed: bool = False,
    archived: bool = False,
) -> KeepList:
    """gkeepapi.node.Listの代替スタブ。"""
    note = MagicMock()
    note.title = title
    note.items = items if items is not None else []
    note.trashed = trashed
    note.archived = archived
    return cast(KeepList, note)


@pytest.fixture
def base_time() -> datetime.datetime:
    return datetime.datetime(2026, 8, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)
