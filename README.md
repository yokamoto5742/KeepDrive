# KeepDrive

Google Keep のメモを Google ドキュメントへコピーし、Google ドライブ上の同名ドキュメントへ
結合する Windows 向けバッチツールです。

Keep の操作はログイン済みのローカル Chrome を Playwright で自動操作して行うため、
Keep 用の認証情報は不要です。

## 動作環境

- Windows 11 / Python 3.13 以上
- プロジェクト配下の仮想環境（`.venv`）
- Google Chrome（Keep にログイン済み）

## セットアップ

### 1. 依存パッケージのインストール

```bash
uv sync
```

CDP で既存の Chrome に接続するため、`playwright install` は不要です。

### 2. Drive / Docs API の認証情報を配置する

1. Google Cloud コンソールで Drive API と Docs API を有効化する
2. 「OAuth クライアント ID」を**デスクトップアプリ**として作成する
3. ダウンロードした JSON を `credentials.json` としてプロジェクトルートに置く

初回実行時のみブラウザが開いて認証を求められ、成功すると `token.json` が生成されます。
以降は `token.json` が再利用されるため、ブラウザ認証は不要です。

### 3. 対象のメモタイトルを指定する

`utils/config.ini` の `[KEEP]` セクションを編集します。

```ini
[KEEP]
# 対象メモのタイトルをカンマ区切りで指定する
target_memo = 人間関係
```

### 4. Chrome をデバッグポート付きで起動する

起動中の Chrome があると同じポートを開けないため、いったん終了してから実行します。

```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

この Chrome で Google Keep にログインした状態にしておきます。

## 実行

```bash
run.bat
```

または直接:

```bash
.venv\Scripts\python.exe main.py
```

終了コードは全件成功で `0`、1件でも失敗した場合は `1` です。

## 処理内容

`target_memo` に指定した各タイトルについて、以下を順に行います。

1. Drive 全体から同名の Google ドキュメントを検索して控えておく
2. Keep で該当メモを開き、「Google ドキュメントにコピー」を実行する
3. Drive をポーリングし、新しく増えたドキュメント（＝コピー）を特定する
4. 同名の既存ドキュメントが**ない**場合は、コピーをそのまま残して終了する
5. ある場合は、既存ドキュメントの末尾にコピーの本文を追記する
6. **結合が成功した場合のみ**、コピーをゴミ箱へ移動する

## 定期実行（Windows タスクスケジューラ）

| 項目 | 設定値 |
| --- | --- |
| トリガー | 毎日 23:00 など |
| プログラム/スクリプト | `C:\Path\To\KeepDrive\run.bat` |
| 開始（オプション） | `C:\Path\To\KeepDrive\` |

「コンピューターを AC 電源で使用している場合のみタスクを開始する」のチェックは外してください。

デバッグポート付きの Chrome が起動している必要があるため、タスクスケジューラで実行する場合は
Chrome の起動も併せて自動化してください。

## テスト

```bash
# 全件
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

# カバレッジ付き
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short --cov=app --cov-report=html
```

## ログ

`logs/KeepDrive.log` に出力され、`utils/config.ini` の `log_retention_days` に従って
日次ローテーションと古いログの削除が行われます。

## 補足

- Google Keep には個人アカウント（`@gmail.com`）向けの公式 API がないため、ブラウザ自動化で
  操作しています。Keep の UI 変更で動作しなくなる可能性があります。
- `credentials.json` / `token.json` は Git 管理対象外です。
