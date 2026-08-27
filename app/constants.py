from typing import Final

# 環境変数キー
ENV_KEEP_EMAIL: Final[str] = 'KEEP_EMAIL'
ENV_KEEP_MASTER_TOKEN: Final[str] = 'KEEP_MASTER_TOKEN'

# 設定ファイル
CONFIG_SECTION_KEEP: Final[str] = 'KEEP'
CONFIG_KEY_TARGET_LISTS: Final[str] = 'target_lists'

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
