# 変更履歴

このプロジェクトのすべての重要な変更は、このファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
バージョン番号は [Semantic Versioning](https://semver.org/lang/ja/) に従っています。

## [Unreleased]

[1.0.1] 2026-09-01

### 修正
- `run.bat`（`pythonw.exe`）起動時にログが1行も残らない問題を修正。`sys.stdout` が `None` の場合はコンソールハンドラを追加しないようにした
- 設定ファイルを読めないときに障害の記録が残らない問題を修正。`main.run()` で設定読み込みより先にログを初期化するようにした
- CDP 接続に失敗したとき、自動起動したヘッドレス Chrome が孤児プロセスとして残る問題を修正
- 本文削除に失敗したとき、Keep のメモが開いたまま残る問題を修正
- 重複行の除去によって生じる連続した空行を畳むようにした

### 変更
- `utils/config.ini` を Git 管理外にし、`utils/config.ini.example` を追加（個人のドキュメント URL がリポジトリに含まれないようにした）
- `utils/log_rotation.py` の設定取得を `configparser` の `fallback` 引数に置き換え、`# type: ignore` を解消
- `KEEP_CARET_SETTLE_SECONDS` / `DOCS_SAVE_POLL_INTERVAL_SECONDS` を実際の単位に合わせて `KEEP_CARET_SETTLE_MS` / `DOCS_SAVE_POLL_INTERVAL_MS` に改名
- 待機処理を `page.wait_for_timeout()` に統一（Playwright 接続前の `chrome_session` を除く）

### 削除
- 未使用コードを削除: `ConfigManager` クラス、`get_config_value()`、`setup_debug_logging()`、`get_log_info()`
- `append_text()` の追記前エクスポート取得（保存確認に不要だったため、HTTP リクエストが1回減少）

## [1.0.0] - 2026-09-01
- 安定版初回リリース