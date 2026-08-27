"""公式Google Keep APIが個人アカウントで利用できるかを検証するスクリプト。

書き換え実装に着手する前に、下記3点を実際のAPI呼び出しで確定させる。
  1. keepスコープでOAuth同意を通せるか
  2. notes.listでメモを取得できるか（Workspace限定制約の実地確認）
  3. 空のリストメモをnotes.createで作成できるか（「空にする」代替手段の可否）
"""

import json
import sys
from pathlib import Path
from typing import Any, cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.paths import CREDENTIALS_PATH

KEEP_SCOPES: list[str] = ['https://www.googleapis.com/auth/keep']

# 既存のtoken.jsonを壊さないよう検証専用のトークンファイルを使う
PROBE_TOKEN_PATH: Path = CREDENTIALS_PATH.parent / 'token_keep_probe.json'

PROBE_NOTE_TITLE: str = 'KeepDrive API検証用メモ（削除して構いません）'


def main() -> int:
    print('=== Google Keep API 検証 ===\n')

    credentials = _step1_authorize()
    if credentials is None:
        return 1

    keep = build('keep', 'v1', credentials=credentials, cache_discovery=False)

    list_ok = _step2_list_notes(keep)
    create_ok = _step3_create_empty_note(keep)

    return _report(list_ok, create_ok)


def _step1_authorize() -> Credentials | None:
    """keepスコープ単体でOAuth同意を通す。ここで弾かれれば以降は実行不能。"""
    print('[1/3] keepスコープでのOAuth認証')

    if not CREDENTIALS_PATH.exists():
        print(f'  NG credentials.jsonが見つかりません: {CREDENTIALS_PATH}')
        return None

    try:
        credentials = _load_or_run_flow()
    except Exception as e:
        print(f'  NG 認証に失敗しました: {type(e).__name__}: {e}')
        print('     → 同意画面にKeepのスコープが表示されなかった場合、')
        print('       個人アカウントではKeep APIを利用できないことが確定する')
        return None

    granted = credentials.scopes or []
    print(f'  OK 認証成功（付与されたスコープ: {granted}）')

    if not any('/auth/keep' in scope for scope in granted):
        print('  NG keepスコープが付与されていません')
        return None

    return credentials


def _load_or_run_flow() -> Credentials:
    if PROBE_TOKEN_PATH.exists():
        credentials = Credentials.from_authorized_user_file(
            str(PROBE_TOKEN_PATH), KEEP_SCOPES
        )
        if credentials.valid:
            return credentials
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            _save(credentials)
            return credentials

    print('  ブラウザで認証画面を開きます...')
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_PATH), KEEP_SCOPES
    )
    credentials = cast(Credentials, flow.run_local_server(port=0))
    _save(credentials)
    return credentials


def _save(credentials: Credentials) -> None:
    PROBE_TOKEN_PATH.write_text(credentials.to_json(), encoding='utf-8')


def _step2_list_notes(keep: Any) -> bool:
    """notes.listを1回だけ呼ぶ。403ならWorkspace限定制約に阻まれている。"""
    print('\n[2/3] notes.list の呼び出し')

    try:
        response = keep.notes().list(pageSize=10).execute()
    except HttpError as e:
        _print_http_error(e)
        return False
    except Exception as e:
        print(f'  NG 予期しないエラー: {type(e).__name__}: {e}')
        return False

    notes = response.get('notes', [])
    print(f'  OK 取得成功（{len(notes)}件）')
    for note in notes:
        kind = 'リスト' if 'list' in note.get('body', {}) else 'テキスト'
        title = note.get('title') or '(無題)'
        print(f'     - [{kind}] {title} / {note.get("name")}')
    return True


def _step3_create_empty_note(keep: Any) -> bool:
    """空リストメモを作成できるか確認する。作成できた場合は必ず削除する。"""
    print('\n[3/3] 空のリストメモの作成')

    name = _try_create(keep, {'list': {'listItems': []}}, 'アイテム0件')
    if name is None:
        # 0件が拒否された場合、create自体の可否を切り分けるため1件で再試行する
        name = _try_create(
            keep,
            {'list': {'listItems': [{'text': {'text': 'dummy'}}]}},
            'アイテム1件',
        )
        if name is None:
            return False
        print('  △ 空リストは作成できないが、1件入りのリストは作成できる')

    _delete_note(keep, name)
    return True


def _try_create(keep: Any, body: dict, label: str) -> str | None:
    try:
        created = keep.notes().create(
            body={'title': PROBE_NOTE_TITLE, 'body': body}
        ).execute()
    except HttpError as e:
        print(f'  NG {label}での作成に失敗')
        _print_http_error(e)
        return None

    print(f'  OK {label}で作成成功: {created.get("name")}')
    return created.get('name')


def _delete_note(keep: Any, name: str) -> None:
    try:
        keep.notes().delete(name=name).execute()
        print(f'  OK 検証用メモを削除しました: {name}')
    except HttpError as e:
        print(f'  ! 検証用メモの削除に失敗。手動で削除してください: {name}')
        _print_http_error(e)


def _print_http_error(error: HttpError) -> None:
    status = error.resp.status if error.resp is not None else '不明'
    print(f'  NG HTTP {status}')
    try:
        detail = json.loads(error.content.decode('utf-8'))
        print(json.dumps(detail, ensure_ascii=False, indent=4))
    except (ValueError, AttributeError, UnicodeDecodeError):
        print(f'     {error.content!r}')


def _report(list_ok: bool, create_ok: bool) -> int:
    print('\n=== 結果 ===')
    print(f'  notes.list  : {"OK" if list_ok else "NG"}')
    print(f'  notes.create: {"OK" if create_ok else "NG"}')

    if list_ok and create_ok:
        print('\n公式Keep APIへの完全書き換えが可能。実装計画に進める。')
        return 0

    print('\n公式Keep APIは利用できない。代替案の検討が必要。')
    return 1


if __name__ == '__main__':
    sys.exit(main())
