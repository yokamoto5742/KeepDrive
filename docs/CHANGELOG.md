# 変更履歴

このプロジェクトのすべての重要な変更は、このファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
バージョン番号は [Semantic Versioning](https://semver.org/lang/ja/) に従っています。

## [Unreleased]

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
