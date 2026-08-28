from typing import Final

# 設定ファイル
CONFIG_SECTION_KEEP: Final[str] = 'KEEP'
CONFIG_KEY_TARGET_MEMO: Final[str] = 'target_memo'

# Google API
DRIVE_DOCUMENT_MIME_TYPE: Final[str] = 'application/vnd.google-apps.document'
GOOGLE_API_SCOPES: Final[list[str]] = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
]

# 認証メッセージ
MSG_CREDENTIALS_NOT_FOUND: Final[str] = 'credentials.jsonが見つかりません: {path}'
MSG_OAUTH_BROWSER_START: Final[str] = 'ブラウザで Google の認証画面を開きます'
MSG_TOKEN_SAVED: Final[str] = '認証トークンを保存しました: {path}'

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
MSG_FATAL_ERROR: Final[str] = '処理を中断しました: {error}'
