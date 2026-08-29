# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## コマンド

Windows 前提。仮想環境の Python を明示的に指定する（`python` / `py` は使わない）。

```bash
# 実行（デバッグポートの Chrome が無ければ自動起動する）
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
  ├ utils/config_manager   … utils/config.ini の読み込み（[KEEP] メモタイトル = 結合先ドキュメントURL）
  ├ service/chrome_session … Playwright でローカル Chrome に CDP 接続（未起動ならヘッドレスで自動起動）し、共有ページを提供
  ├ service/keep_browser   … Keep を操作してメモをコピーし、コピー先ドキュメントの URL を返す／結合後にメモ本文を削除する
  ├ service/docs_browser   … Google ドキュメントの本文取得・追記・ゴミ箱移動
  └ service/keep_doc_merge … メモごとに keep_browser → docs_browser を呼ぶ
```

- **Google API（OAuth）は使わない。** すべてログイン済みローカル Chrome のブラウザ操作（RPA）で行う。Google の審査未完了アプリでの `エラー 403: access_denied` を回避するための設計なので、Drive/Docs API への差し戻しは提案しない。
- ドキュメント本文の取得だけは DOM ではなく `export?format=txt` を `page.request` で取得する（ブラウザのセッションCookieをそのまま使うため認証不要）。
- `main.run()` はメモ1件ごとに例外を握りつぶす。1件の失敗で全体を止めないための意図的な設計。
- **追記がドライブに保存されたことを確認できた場合のみ** コピーをゴミ箱へ移動し、その後で Keep メモの本文を削除する。この順序を入れ替えるとデータ消失につながる。
- 追記するのは結合先ドキュメントに存在しない行だけ。`keep_doc_merge._remove_duplicate_lines()` が完全一致の行（前後の空白は無視）を落とす。結合先ドキュメントの既存本文は書き換えない。
- 終了コードは全件成功で `0`、1件でも失敗すれば `1`。

## 制約・落とし穴

- 公式 Google Keep API（`keep.googleapis.com`）は**個人 @gmail.com アカウントでは利用できない**（`invalid_scope`、Workspace 限定）。Keep API への移行提案はしない。詳細は `docs/Google Keep API移行検証記録.md`。
- CDP 接続先は `http://127.0.0.1:9222`。`localhost` は IPv6（`::1`）に解決されることがあり、IPv4 のみで待ち受ける Chrome に繋がらない。
- Chrome 136 以降は**デフォルトプロファイルだと `--remote-debugging-port` が黙って無視される**。`chrome_session.launch_chrome()` は専用プロファイル `%LocalAppData%\KeepDrive\ChromeProfile` で起動する。このプロファイルは初回のみ手動で Google ログインが必要（普段使いの Chrome とは別物なので、同時起動しても競合しない）。
- 自動起動する Chrome は**ヘッドレス**（`--headless=new`）。ヘッドレスではログイン操作ができないため、専用プロファイルのログインが切れると `MSG_KEEP_LOGIN_REQUIRED` で失敗する。復旧するには `CHROME_LAUNCH_ARGS` から `--headless=new` を一時的に外して起動し、ログインし直す。
- **終了するのは自分で起動した Chrome だけ。** 既に `9222` で待ち受けている Chrome に接続した場合は CDP を切断するだけで終了しない（ユーザーが手動で開いている Chrome を閉じないため）。`connect_chrome()` は起動した場合のみ `Popen` を返し、`_close_session()` がその判定に使う。
- セレクタは Keep の DOM（`div[tabindex="0"]` のカード、`その他` ボタン、`Google ドキュメントにコピー` メニュー、コピー完了通知の `開く`、メモ本文の `div[role="combobox"][contenteditable="true"]`、`閉じる` ボタン）と Google ドキュメントの DOM（`.kix-appview-editor`、`ファイル` / `ゴミ箱に移動` メニュー）に依存する。UI 変更や表示言語の違いで壊れるため、ラベルは `app/constants.py` で調整する。
- 追記直後はドライブへの保存が終わっていない。`docs_browser._wait_until_saved()` がエクスポートを再取得して反映を確認する。

## コード規約（`.claude/rules/` の補足）

- ユーザー向けメッセージ・URL・セレクタ・画面ラベルはすべて `app/constants.py` に `Final` で定義し、モジュール側では参照のみ行う。文字列リテラルを直書きしない。
- テストは MagicMock で Playwright の `Page` を差し替える。実際のブラウザには接続しない。

## Git

- `main` に直接コミットする（ブランチは切らない）。
- コミットメッセージは絵文字付き Conventional Commits + 日本語。例: `✨ feat(constants): マスタートークン取得・認証用のデバイスIDを追加`
- 変更は `docs/CHANGELOG.md`（Keep a Changelog 形式）に記録する。
