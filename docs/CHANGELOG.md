# 変更履歴

このプロジェクトのすべての重要な変更は、このファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
バージョン番号は [Semantic Versioning](https://semver.org/lang/ja/) に従っています。

## [Unreleased]

### 追加
- `service/keep_doc_merge.py` を追加。`utils/config.ini` の `[KEEP] target_memo`（カンマ区切り）で指定したタイトルの Keep メモを Playwright で「Google ドキュメントにコピー」し、同名の既存ドキュメント末尾へ結合したうえでコピーをゴミ箱へ移動する
- `service/keep_browser.py` を追加。起動済みローカル Chrome へ CDP（`http://localhost:9222`）で接続し、ログイン済みプロファイルのまま Keep を操作する
- `service/drive_client.py` に `find_document_ids_by_name` / `trash_file` を追加
- `service/docs_client.py` に `extract_text` を追加
- `utils/config_manager.py` に `get_target_memo_titles` を追加

### 変更
- `main.py` の `run()` を Keep メモの Google ドキュメント結合処理に置き換え（gkeepapi ベースの同期処理から全面的に移行）
- `pyproject.toml` に `playwright` を追加

### 削除
- gkeepapi によるKeep操作を全面的に廃止。`service/keep_client.py` / `service/sync_service.py` / `scripts/get_keep_token.py` / `utils/env_loader.py` と対応するテストを削除
- 依存パッケージから `gkeepapi` / `gpsoauth` / `python-dotenv` を削除（`.env` のマスタートークンは不要になった）
- `utils/config.ini` の `[KEEP] target_lists` と `utils/config_manager.get_target_list_names` を削除
- 未使用になった `service/drive_client.py` の `find_or_create_folder` / `find_or_create_document`、`app/paths.py` の `KEEP_STATE_PATH`、`app/constants.py` の Keep 認証・同期関連定数を削除

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
