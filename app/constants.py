from typing import Final

# 設定ファイル
CONFIG_SECTION_KEEP: Final[str] = 'KEEP'

# ブラウザ操作（Playwright）
# localhostはIPv6（::1）に解決されることがあり、IPv4のみで待ち受けるChromeに繋がらない
CHROME_CDP_URL: Final[str] = 'http://127.0.0.1:9222'
BROWSER_TIMEOUT_MS: Final[int] = 30000
DIALOG_TIMEOUT_MS: Final[int] = 5000

# Chrome未起動時の自動起動設定
CHROME_EXECUTABLE_PATHS: Final[tuple[str, ...]] = (
    r'%ProgramFiles%\Google\Chrome\Application\chrome.exe',
    r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe',
    r'%LocalAppData%\Google\Chrome\Application\chrome.exe',
)
# Chrome 136以降はデフォルトプロファイルだと--remote-debugging-portが無視されるため、
# 専用のユーザーデータディレクトリで起動する（初回のみGoogleへのログインが必要）
CHROME_USER_DATA_DIR: Final[str] = r'%LocalAppData%\KeepDrive\ChromeProfile'
CHROME_LAUNCH_ARGS: Final[tuple[str, ...]] = (
    '--remote-debugging-port=9222',
    '--user-data-dir={user_data_dir}',
    '--headless=new',
    # ヘッドレスの既定ウィンドウは狭く、Keepのカード配置が崩れるため明示する
    '--window-size=1920,1080',
    '--no-first-run',
    '--no-default-browser-check',
)
CHROME_LAUNCH_POLL_INTERVAL_SECONDS: Final[float] = 1.0
CHROME_LAUNCH_MAX_ATTEMPTS: Final[int] = 15
CHROME_CLOSE_TIMEOUT_SECONDS: Final[float] = 5.0

# Google Keep のDOM依存値
KEEP_SEARCH_URL: Final[str] = 'https://keep.google.com/#search/text={query}'
# メモカードはrole="listitem"を持たないため、フォーカス可能なカード要素で特定する
KEEP_NOTE_CARD_SELECTOR: Final[str] = 'div[tabindex="0"]'
KEEP_LOGIN_URL_PREFIX: Final[str] = 'https://accounts.google.com'
KEEP_MORE_MENU_LABEL: Final[str] = 'その他'
KEEP_COPY_TO_DOCS_LABEL: Final[str] = 'Google ドキュメントにコピー'
KEEP_OPEN_COPIED_DOC_LABEL: Final[str] = '開く'
KEEP_NOTE_BODY_LABEL: Final[str] = 'メモ'
KEEP_CLOSE_NOTE_LABEL: Final[str] = '閉じる'

# Google ドキュメントのDOM依存値
DOCS_URL_PATTERN: Final[str] = r'/document/d/([\w-]+)'
DOCS_URL_GLOB: Final[str] = 'https://docs.google.com/document/**'
DOCS_EXPORT_URL: Final[str] = (
    'https://docs.google.com/document/d/{document_id}/export?format=txt'
)
DOCS_EDITOR_SELECTOR: Final[str] = '.kix-appview-editor'
DOCS_FILE_MENU_LABEL: Final[str] = 'ファイル'
DOCS_MOVE_TO_TRASH_LABEL: Final[str] = 'ゴミ箱に移動'

# 追記がドライブへ保存されるまでのポーリング設定
DOCS_SAVE_POLL_INTERVAL_SECONDS: Final[float] = 2.0
DOCS_SAVE_POLL_MAX_ATTEMPTS: Final[int] = 10

# ブラウザ接続メッセージ
MSG_CHROME_CONNECTED: Final[str] = 'ローカルのChromeに接続しました: {url}'
MSG_CHROME_CONNECT_FAILED: Final[str] = (
    'Chromeに接続できません（{url}）。'
    'リモートデバッグなしのChromeが起動中の場合は、'
    'Chromeをすべて終了してから再実行してください: {error}'
)
MSG_CHROME_LAUNCHING: Final[str] = (
    'Chromeに接続できないため、リモートデバッグを有効にして起動します: {path}'
)
MSG_CHROME_NOT_FOUND: Final[str] = (
    'Chromeの実行ファイルが見つかりません。確認した場所: {paths}'
)
MSG_CHROME_CLOSED: Final[str] = '起動したChromeを終了しました'
MSG_CHROME_CLOSE_FAILED: Final[str] = 'Chromeの終了に失敗しました: {error}'

# Keep操作メッセージ
MSG_MEMO_NOT_FOUND: Final[str] = 'Keepに指定タイトルのメモが見つかりません: {title}'
MSG_MEMO_COPIED: Final[str] = 'メモ「{title}」をGoogleドキュメントにコピーしました'
MSG_COPIED_DOC_NOT_OPENED: Final[str] = (
    'コピー完了通知の「{label}」を押せず、コピー先ドキュメントを特定できません: {title}'
)
MSG_KEEP_LOGIN_REQUIRED: Final[str] = (
    'Keepを開けずログイン画面へ遷移しました。'
    'app/constants.pyのCHROME_LAUNCH_ARGSから--headless=newを一時的に外して起動し、'
    '専用プロファイルでGoogleにログインし直してください'
)
MSG_MEMO_BODY_CLEARED: Final[str] = (
    'メモ「{title}」の本文を削除しました（タイトルは残しています）'
)
MSG_MEMO_BODY_NOT_CLEARED: Final[str] = 'メモ「{title}」の本文を削除できませんでした'

# ドキュメント操作メッセージ
MSG_INVALID_DOCUMENT_URL: Final[str] = (
    'GoogleドキュメントのURLとして認識できません: {url}'
)
MSG_DOCUMENT_FETCH_FAILED: Final[str] = (
    'ドキュメント本文を取得できませんでした（HTTP {status}）: {url}'
)
MSG_APPEND_NOT_SAVED: Final[str] = (
    '追記内容がドキュメントに保存されたことを確認できません: {url}'
)

# 結合処理メッセージ
MSG_MERGE_START: Final[str] = 'Keepメモのドキュメント結合処理を開始します'
MSG_NO_TARGET_MEMO: Final[str] = (
    'config.iniの[KEEP]セクションに「メモタイトル = 結合先ドキュメントURL」が'
    '設定されていません'
)
MSG_MEMO_START: Final[str] = 'メモ「{title}」の処理を開始します'
MSG_MERGE_SUCCESS: Final[str] = '既存ドキュメント「{title}」に内容を結合しました'
MSG_DUPLICATE_LINES_SKIPPED: Final[str] = (
    'メモ「{title}」の重複行{count}件を追記対象から除外しました'
)
MSG_NO_NEW_CONTENT: Final[str] = (
    'メモ「{title}」の内容はすべて既存ドキュメントと重複するため追記しません'
)
MSG_COPIED_DOC_TRASHED: Final[str] = (
    'コピーしたドキュメントをゴミ箱へ移動しました: {title}'
)
MSG_MEMO_MERGE_FAILED: Final[str] = 'メモ「{title}」の処理に失敗しました: {error}'
MSG_MERGE_COMPLETED: Final[str] = (
    '結合処理が完了しました（成功: {success}件 / 失敗: {failure}件）'
)
MSG_FATAL_ERROR: Final[str] = '処理を中断しました: {error}'
