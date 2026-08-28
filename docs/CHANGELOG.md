# 変更履歴

このプロジェクトのすべての重要な変更は、このファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
バージョン番号は [Semantic Versioning](https://semver.org/lang/ja/) に従っています。

## [Unreleased]

### 追加
- `service/keep_doc_merge.py` を追加。`utils/config.ini` の `[KEEP]` で指定したメモを Playwright で「Google ドキュメントにコピー」し、結合先ドキュメントの末尾へ追記したうえでコピーをゴミ箱へ移動する
- `service/keep_browser.py` を追加。Keep を操作し、コピー完了通知の「開く」から新しいタブを開いてコピー先ドキュメントの URL を取得する
- `service/docs_browser.py` を追加。Google ドキュメントをブラウザ操作し、テキストエクスポート（`export?format=txt`）での本文取得、末尾への追記、ファイルメニューからのゴミ箱移動を行う
- `service/chrome_session.py` を追加。起動済みローカル Chrome へ CDP（`http://localhost:9222`）で接続し、ログイン済みプロファイルのまま Keep とドキュメントを1つのページで操作する
- `utils/config_manager.py` に `get_merge_targets` と `CaseSensitiveConfigParser` を追加。`[KEEP]` セクションの「メモタイトル = 結合先ドキュメントURL」を大文字小文字そのままで読み取る
- 追記後にエクスポートを再取得して保存反映を確認する処理を追加。確認できるまでコピーをゴミ箱へ移動しない

### 変更
- `main.py` の `run()` を Keep メモの Google ドキュメント結合処理に置き換え（gkeepapi ベースの同期処理から全面的に移行）
- Drive / Docs API（OAuth）による操作を全廃し、ログイン済みローカル Chrome のブラウザ操作（RPA）に置き換え。Google の審査未完了アプリで発生する `エラー 403: access_denied` を回避する
- 結合先ドキュメントの特定方法を Drive 検索から設定ファイルの URL 指定へ変更。`utils/config.ini` の `[KEEP]` は「メモタイトル = 結合先ドキュメントURL」形式になった
- `pyproject.toml` に `playwright` を追加

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
