# 変更履歴

このプロジェクトのすべての重要な変更は、このファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
バージョン番号は [Semantic Versioning](https://semver.org/lang/ja/) に従っています。

## [Unreleased]

### 追加
- `service/keep_browser.py` に `read_note_body` を追加。メモを開いて本文テキストを取得し、そのまま閉じる（編集はしない）
- 本文が空のメモは何もせずスキップする処理を `service/keep_doc_merge.py` に追加（`MSG_MEMO_BODY_EMPTY`）。ドキュメントへのコピー・追記・コピーの削除・本文削除をいずれも行わない
- 追記前に重複行を除外する処理を `service/keep_doc_merge.py` に追加。コピーしたメモの各行のうち、結合先ドキュメントに完全一致の行が既にあるものと、コピー内で重複する行を追記対象から外す（空行は段落の区切りとして残す）。除外の結果、追記する内容が空になった場合は追記せずコピーの削除とメモ本文の削除だけを行う
- `service/keep_browser.py` に `clear_note_body` を追加。結合が完了したメモを開いて本文だけを削除する（次回の登録に備えてタイトルは残す）
- `service/keep_browser.py` に Keep がログイン画面へ遷移した場合の判定を追加。ヘッドレスではログインできないため、ヘッドレスを外して起動し直す案内を出す
- `service/chrome_session.py` に自動起動した Chrome の終了処理を追加。CDP の `Browser.close` を送ったあとプロセスの終了を待ち、残っていれば強制終了する（手動起動の Chrome に接続した場合は切断のみで終了しない）

### 変更
- 自動起動する Chrome をヘッドレス（`--headless=new`）にした。ヘッドレスの既定ウィンドウでは Keep のカード配置が崩れるため `--window-size=1920,1080` も指定する
- `service/chrome_session.py` の `connect_chrome` が `(Browser, Popen | None)` を返すようになった。自分で起動した Chrome だけを終了するための判定に使う
- `service/keep_browser.py` のメモカード検索を `_find_note_card` に切り出し、コピー処理と本文削除処理で共有する
- 進行状況をコマンドプロンプトで確認できるように、コンソールへのログ出力レベルを `WARNING` から設定ファイルのログレベル（既定 `INFO`）へ変更した。出力先は標準出力、形式は `時刻 メッセージ` の簡潔なものにする
- メモの処理開始ログを `service/keep_doc_merge.py` から `main.py` の `run()` へ移し、`[1/8]` のように全体の進捗が分かるようにした（`MSG_MEMO_START`）

### 修正
- 空の結合先ドキュメントへ追記すると 1 行目が空行になっていた問題を修正。追記テキストの先頭に付ける区切りの改行を、結合先に既存の本文がある場合だけ付けるようにした（`_with_separator`）
- 本文削除が `メモ「{title}」の本文を削除できませんでした` で断続的に失敗していた問題を修正（8件中4件が失敗していた）。本文をクリックした直後は Keep が非同期にキャレットを置き直すため、間を置かずに `Control+A` を押すと選択が解除され、続く `Delete` が空振り（キャレット位置によっては1文字だけ削除）していた。クリック後に `KEEP_CARET_SETTLE_SECONDS` 待ってから全選択し、削除できるまで `KEEP_CLEAR_BODY_MAX_ATTEMPTS` 回まで再試行する
- ヘッドレス実行時に本文削除が `Locator.wait_for: Timeout 30000ms exceeded`（`get_by_role("textbox", name="メモ")`）で失敗していた問題を修正。現在の Keep のメモ本文は `aria-label` を持たない `role="combobox"`（オートコンプリート付き）で、`role="textbox"` の名前「メモ」では特定できないため、`KEEP_NOTE_BODY_SELECTOR`（`div[role="combobox"][contenteditable="true"]`）で特定する。タイトルは `role="textbox"` のままなので巻き込まない

## [1.1.0] - 2026-08-28

### 追加
- `service/keep_doc_merge.py` を追加。`utils/config.ini` の `[KEEP]` で指定したメモを Playwright で「Google ドキュメントにコピー」し、結合先ドキュメントの末尾へ追記したうえでコピーをゴミ箱へ移動する
- `service/keep_browser.py` を追加。Keep を操作し、コピー完了通知の「開く」から新しいタブを開いてコピー先ドキュメントの URL を取得する
- `service/docs_browser.py` を追加。Google ドキュメントをブラウザ操作し、テキストエクスポート（`export?format=txt`）での本文取得、末尾への追記、ファイルメニューからのゴミ箱移動を行う
- `service/chrome_session.py` を追加。起動済みローカル Chrome へ CDP（`http://localhost:9222`）で接続し、ログイン済みプロファイルのまま Keep とドキュメントを1つのページで操作する
- `utils/config_manager.py` に `get_merge_targets` と `CaseSensitiveConfigParser` を追加。`[KEEP]` セクションの「メモタイトル = 結合先ドキュメントURL」を大文字小文字そのままで読み取る
- 追記後にエクスポートを再取得して保存反映を確認する処理を追加。確認できるまでコピーをゴミ箱へ移動しない
- `service/chrome_session.py` に Chrome の自動起動を追加。CDP 接続に失敗した場合はリモートデバッグ有効の Chrome を起動し、接続できるまでポーリングする（`ConnectionError: connect ECONNREFUSED ::1:9222` の対策）

### 変更
- `main.py` の `run()` を Keep メモの Google ドキュメント結合処理に置き換え（gkeepapi ベースの同期処理から全面的に移行）
- Drive / Docs API（OAuth）による操作を全廃し、ログイン済みローカル Chrome のブラウザ操作（RPA）に置き換え。Google の審査未完了アプリで発生する `エラー 403: access_denied` を回避する
- 結合先ドキュメントの特定方法を Drive 検索から設定ファイルの URL 指定へ変更。`utils/config.ini` の `[KEEP]` は「メモタイトル = 結合先ドキュメントURL」形式になった
- `pyproject.toml` に `playwright` を追加
- CDP 接続先を `http://localhost:9222` から `http://127.0.0.1:9222` へ変更。`localhost` が IPv6（`::1`）に解決されると、IPv4 のみで待ち受ける Chrome に接続できないため
- Chrome の自動起動は専用プロファイル `%LocalAppData%\KeepDrive\ChromeProfile` を使う。Chrome 136 以降はデフォルトプロファイルだと `--remote-debugging-port` が無視されるため（このプロファイルは初回のみ手動で Google ログインが必要）

### 修正
- Keep のメモカードを `role="listitem"` で探していたため、メモが表示されていても「Keepに指定タイトルのメモが見つかりません」で失敗していた問題を修正。現在の Keep の DOM には `listitem` ロールが存在しないため、`KEEP_NOTE_CARD_SELECTOR`（`div[tabindex="0"]`）でカードを特定する

### 削除
- gkeepapi によるKeep操作を全面的に廃止。`service/keep_client.py` / `service/sync_service.py` / `scripts/get_keep_token.py` / `utils/env_loader.py` と対応するテストを削除
- OAuth 認証と API 呼び出しの `service/google_auth.py` / `service/drive_client.py` / `service/docs_client.py`、認証情報のパスのみを持つ `app/paths.py` と対応するテストを削除（`credentials.json` / `token.json` は不要になった）
- 依存パッケージから `gkeepapi` / `gpsoauth` / `python-dotenv` / `google-api-python-client` / `google-auth` / `google-auth-httplib2` / `google-auth-oauthlib` を削除
- `utils/config.ini` の `[KEEP] target_lists` / `[KEEP] target_memo` と `utils/config_manager` の `get_target_list_names` / `get_target_memo_titles` を削除
- `app/constants.py` の Keep 認証・同期関連定数と OAuth / Drive 関連定数を削除

## [1.0.0] - 2026-08-27

### 追加
- Google Keep のリストメモを Google ドライブの同名ドキュメントへ追記し、元のメモを空にする本体処理を実装
- `utils/config.ini` の `[KEEP] target_lists` で取り込むリスト名を指定する機能を追加（空欄時は全リストが対象）
- OAuth 2.0 による Drive / Docs API 認証（`credentials.json` / `token.json`）を実装
- Keep マスタートークン取得用のセットアップスクリプト `scripts/get_keep_token.py` を追加
- タスクスケジューラ向け起動バッチ `run.bat` を追加

### 変更
- `utils/config.ini` の `project_name` を `KeepDrive` に変更
- `pyproject.toml` に実行時依存パッケージを追加（`gkeepapi`、`google-api-python-client`、`gpsoauth`、`python-dotenv` ほか）
- `.gitignore` に `credentials.json` / `token.json` / `.gkeep_token` を追加

## [0.0.1] - 2026-08-27
- リポジトリの初期設定
