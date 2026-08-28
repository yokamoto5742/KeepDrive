from typing import Final

# 環境変数キー
ENV_KEEP_EMAIL: Final[str] = 'KEEP_EMAIL'
ENV_KEEP_MASTER_TOKEN: Final[str] = 'KEEP_MASTER_TOKEN'

# マスタートークン取得時と認証時で同一のデバイスIDを使う必要がある
KEEP_DEVICE_ID: Final[str] = '0123456789abcdef'

# 設定ファイル
CONFIG_SECTION_KEEP: Final[str] = 'KEEP'
CONFIG_KEY_TARGET_LISTS: Final[str] = 'target_lists'
CONFIG_KEY_TARGET_MEMO: Final[str] = 'target_memo'

# Google API
DRIVE_FOLDER_MIME_TYPE: Final[str] = 'application/vnd.google-apps.folder'
DRIVE_DOCUMENT_MIME_TYPE: Final[str] = 'application/vnd.google-apps.document'
GOOGLE_API_SCOPES: Final[list[str]] = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
]

# 認証メッセージ
MSG_ENV_KEY_MISSING: Final[str] = '.envに{key}が設定されていません'
MSG_CREDENTIALS_NOT_FOUND: Final[str] = 'credentials.jsonが見つかりません: {path}'
MSG_OAUTH_BROWSER_START: Final[str] = 'ブラウザで Google の認証画面を開きます'
MSG_TOKEN_SAVED: Final[str] = '認証トークンを保存しました: {path}'
MSG_KEEP_AUTH_SUCCESS: Final[str] = 'Google Keepにログインしました: {email}'
MSG_KEEP_AUTH_FAILED: Final[str] = 'Google Keepのログインに失敗しました: {error}'
MSG_KEEP_STATE_LOAD_FAILED: Final[str] = 'Keepの状態キャッシュを読み込めませんでした。全件同期します: {error}'
MSG_KEEP_STATE_SAVE_FAILED: Final[str] = 'Keepの状態キャッシュを保存できませんでした: {error}'

# 同期処理メッセージ
MSG_TARGET_LISTS_ALL: Final[str] = '取り込み対象リストの指定がないため、全リストを対象にします'
MSG_TARGET_LISTS_SELECTED: Final[str] = '取り込み対象リスト: {names}'
MSG_LIST_NOT_FOUND: Final[str] = '指定されたリストがKeep上に見つかりません: {names}'
MSG_NO_TARGET_NOTES: Final[str] = '処理対象のリストメモがありません'
MSG_NOTE_START: Final[str] = 'リスト「{title}」の処理を開始します（{count}件）'
MSG_APPEND_SUCCESS: Final[str] = 'リスト「{title}」を{count}件ドキュメントへ追記しました'
MSG_CLEAR_SUCCESS: Final[str] = 'リスト「{title}」のアイテムを削除しました'
MSG_NOTE_FAILED: Final[str] = 'リスト「{title}」の処理に失敗しました: {error}'
MSG_FOLDER_CREATED: Final[str] = 'フォルダを作成しました: {name}'
MSG_DOCUMENT_CREATED: Final[str] = 'ドキュメントを作成しました: {name}'

# 実行結果メッセージ
MSG_SYNC_START: Final[str] = 'Keepメモの集約処理を開始します'
MSG_SYNC_COMPLETED: Final[str] = '集約処理が完了しました（成功: {success}件 / 失敗: {failure}件）'
MSG_FATAL_ERROR: Final[str] = '処理を中断しました: {error}'

# ブラウザ操作（Playwright）
CHROME_CDP_URL: Final[str] = 'http://localhost:9222'
BROWSER_TIMEOUT_MS: Final[int] = 30000
KEEP_SEARCH_URL: Final[str] = 'https://keep.google.com/#search/text={query}'
KEEP_MORE_MENU_LABEL: Final[str] = 'その他'
KEEP_COPY_TO_DOCS_LABEL: Final[str] = 'Google ドキュメントにコピー'

# コピー生成をDriveで検知するまでのポーリング設定
DRIVE_POLL_INTERVAL_SECONDS: Final[float] = 2.0
DRIVE_POLL_MAX_ATTEMPTS: Final[int] = 15

# ブラウザ操作メッセージ
MSG_CHROME_CONNECTED: Final[str] = 'ローカルのChromeに接続しました: {url}'
MSG_CHROME_CONNECT_FAILED: Final[str] = (
    'Chromeに接続できません（{url}）。'
    'Chromeを --remote-debugging-port オプション付きで起動してください: {error}'
)
MSG_MEMO_NOT_FOUND: Final[str] = 'Keepに指定タイトルのメモが見つかりません: {title}'
MSG_MEMO_COPIED: Final[str] = 'メモ「{title}」をGoogleドキュメントにコピーしました'

# 結合処理メッセージ
MSG_MERGE_START: Final[str] = 'Keepメモのドキュメント結合処理を開始します'
MSG_NO_TARGET_MEMO: Final[str] = 'config.iniの[KEEP] target_memoが設定されていません'
MSG_MEMO_START: Final[str] = 'メモ「{title}」の処理を開始します'
MSG_COPIED_DOC_NOT_FOUND: Final[str] = (
    'コピーしたドキュメントがGoogleドライブで見つかりません: {title}'
)
MSG_MERGE_TARGET_NOT_FOUND: Final[str] = (
    '同名の既存ドキュメントがないため、コピーしたドキュメントをそのまま残します: {title}'
)
MSG_MERGE_SUCCESS: Final[str] = '既存ドキュメント「{title}」に内容を結合しました'
MSG_COPIED_DOC_TRASHED: Final[str] = (
    'コピーしたドキュメントをゴミ箱へ移動しました: {title}'
)
MSG_MEMO_MERGE_FAILED: Final[str] = 'メモ「{title}」の処理に失敗しました: {error}'
MSG_MERGE_COMPLETED: Final[str] = (
    '結合処理が完了しました（成功: {success}件 / 失敗: {failure}件）'
)
