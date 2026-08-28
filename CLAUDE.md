# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## コマンド

Windows 前提。仮想環境の Python を明示的に指定する（`python` / `py` は使わない）。

```bash
# 実行（事前に Chrome を --remote-debugging-port=9222 付きで起動しておく）
run.bat                                    # または .venv\Scripts\python.exe main.py

# テスト
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
.venv\Scripts\python.exe -m pytest tests/service/test_keep_doc_merge.py -v
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
  ├ utils/config_manager  … utils/config.ini の読み込み（[KEEP] target_memo）
  ├ service/google_auth   … OAuth（credentials.json → token.json）と Drive/Docs サービス生成
  ├ service/keep_browser  … Playwright で起動済みローカル Chrome に CDP 接続し Keep を操作
  └ service/keep_doc_merge … メモごとに keep_browser → drive_client → docs_client を呼ぶ
```

- Keep の操作はブラウザ自動化で行う。ログイン済みの Chrome プロファイルをそのまま使うため、Keep 用の認証情報はコードに持たない。
- `main.run()` はメモ1件ごとに例外を握りつぶす。1件の失敗で全体を止めないための意図的な設計。
- **結合が成功した場合のみ** コピー元ドキュメントをゴミ箱へ移動する。この順序を入れ替えるとデータ消失につながる。
- 終了コードは全件成功で `0`、1件でも失敗すれば `1`。

## 制約・落とし穴

- 公式 Google Keep API（`keep.googleapis.com`）は**個人 @gmail.com アカウントでは利用できない**（`invalid_scope`、Workspace 限定）。Keep API への移行提案はしない。詳細は `docs/Google Keep API移行検証記録.md`。
- Chrome は `--remote-debugging-port=9222` 付きで起動している必要がある。通常起動中の Chrome があるとポートを開けない。
- `service/keep_browser.py` のセレクタは Keep の DOM（`role="listitem"` のカード、`その他` ボタン、`Google ドキュメントにコピー` メニュー）に依存する。Keep の UI 変更や表示言語の違いで壊れるため、ラベルは `app/constants.py` で調整する。
- コピー直後のドキュメントは Drive の検索反映に数秒かかる。`_wait_for_copied_document()` がコピー前後の差分でポーリングして特定する。
- `credentials.json` / `token.json` は Git 管理対象外かつ Claude の編集禁止。生成手順は `README.md` を参照。
- `docs/Google Keep メモ自動集約アプリ.md` は gkeepapi 時代の仕様書で、現在の実装とは一致しない。

## コード規約（`.claude/rules/` の補足）

- ユーザー向けメッセージ・API 定数・設定キーはすべて `app/constants.py` に `Final` で定義し、モジュール側では参照のみ行う。文字列リテラルを直書きしない。
- Google API のサービスオブジェクトは動的生成のため `Any` で受ける（`build_drive_service` / `build_docs_service`）。
- テストは MagicMock で Drive/Docs/Playwright を差し替える。実際の API やブラウザには接続しない。

## Git

- `main` に直接コミットする（ブランチは切らない）。
- コミットメッセージは絵文字付き Conventional Commits + 日本語。例: `✨ feat(constants): マスタートークン取得・認証用のデバイスIDを追加`
- 変更は `docs/CHANGELOG.md`（Keep a Changelog 形式）に記録する。
