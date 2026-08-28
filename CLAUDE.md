# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## コマンド

Windows 前提。仮想環境の Python を明示的に指定する（`python` / `py` は使わない）。

```bash
# 実行
run.bat                                    # または .venv\Scripts\python.exe main.py

# テスト
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
.venv\Scripts\python.exe -m pytest tests/service/test_sync_service.py -v
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short --cov=app --cov-report=html

# 型チェック（standard モード / 対象は app, service, utils, tests）
.venv\Scripts\python.exe -m pyright

# 依存の同期
uv sync
```

コミット前に **pytest 全件パス** と **pyright** の両方を通す。

## アーキテクチャ

`main.py` の `run()` が処理フロー全体の唯一のオーケストレーターで、各層は下位を呼ばない。

```
main.run()
  ├ utils/env_loader, utils/config_manager  … .env と utils/config.ini の読み込み
  ├ service/keep_client   … gkeepapi 認証・リストメモ抽出・アイテム削除
  ├ service/google_auth   … OAuth（credentials.json → token.json）と Drive/Docs サービス生成
  └ service/sync_service  … メモごとに drive_client → docs_client → keep_client を呼ぶ
```

- `sync_service._sync_note()` はメモ1件ごとに例外を握りつぶす。1件の失敗で全体を止めないための意図的な設計なので、外へ伝播させない。
- **追記が成功した場合のみ** Keep のアイテムを削除する。この順序を入れ替えるとデータ消失につながる。
- 終了コードは全件成功で `0`、1件でも失敗すれば `1`。

## 制約・落とし穴

- 公式 Google Keep API（`keep.googleapis.com`）は**個人 @gmail.com アカウントでは利用できない**（`invalid_scope`、Workspace 限定）。非公式クライアント `gkeepapi` からの移行提案はしない。詳細は `docs/Google Keep API移行検証記録.md`。
- Keep 認証にはマスタートークンが必要。`app/constants.py` の `KEEP_DEVICE_ID` は**トークン取得時と認証時で同一の値**でなければならない。
- `.env` / `credentials.json` / `token.json` / `.gkeep_token` は Git 管理対象外かつ Claude の編集禁止。生成手順は `README.md` を参照。
- 各所の docstring が参照する「仕様書 §x」は `docs/Google Keep メモ自動集約アプリ.md`。仕様に関わる変更時はここを確認する。

## コード規約（`.claude/rules/` の補足）

- ユーザー向けメッセージ・API 定数・設定キーはすべて `app/constants.py` に `Final` で定義し、モジュール側では参照のみ行う。文字列リテラルを直書きしない。
- Google API のサービスオブジェクトは動的生成のため `Any` で受ける（`build_drive_service` / `build_docs_service`）。
- テストは `tests/conftest.py` の `make_item` / `make_note` で MagicMock スタブを生成する。gkeepapi の実オブジェクトは組み立てない。

## Git

- `main` に直接コミットする（ブランチは切らない）。
- コミットメッセージは絵文字付き Conventional Commits + 日本語。例: `✨ feat(constants): マスタートークン取得・認証用のデバイスIDを追加`
- 変更は `docs/CHANGELOG.md`（Keep a Changelog 形式）に記録する。
