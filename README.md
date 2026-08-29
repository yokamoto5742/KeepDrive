# KeepDrive

Google Keep のメモを Google ドキュメントへコピーし、指定した結合先ドキュメントへ
追記する Windows 向けバッチツールです。

Keep もドキュメントもログイン済みのローカル Chrome を Playwright で自動操作（RPA）して
処理するため、Google API の OAuth 認証情報は一切不要です。

## 動作環境

- Windows 11 / Python 3.13 以上
- プロジェクト配下の仮想環境（`.venv`）
- Google Chrome（Keep と Google ドキュメントにログイン済み）

## セットアップ

### 1. 依存パッケージのインストール

```bash
uv sync
```

CDP で既存の Chrome に接続するため、`playwright install` は不要です。

### 2. 対象のメモと結合先ドキュメントを指定する

`utils/config.ini` の `[KEEP]` セクションに「メモタイトル = 結合先ドキュメントURL」を
1行ずつ書きます。

```ini
[KEEP]
# メモタイトル = 結合先ドキュメントURL
人間関係 = https://docs.google.com/document/d/xxxxxxxxxxxxxxxxxxxxxxxxxxxx/edit
読書メモ = https://docs.google.com/document/d/yyyyyyyyyyyyyyyyyyyyyyyyyyyy/edit
```

結合先ドキュメントの URL は、Google ドキュメントで対象のファイルを開いたときの
アドレスバーの値をそのまま貼り付けます。

### 3. 自動操作用 Chrome にログインする

デバッグポート（`9222`）の Chrome が起動していない場合、アプリが自動で起動します。
手動で起動しておく必要はありません。

Chrome 136 以降はデフォルトプロファイルだと `--remote-debugging-port` が無視されるため、
専用プロファイル `%LocalAppData%\KeepDrive\ChromeProfile` で起動します。普段使いの Chrome とは
別ウィンドウになるので、**初回だけ** そのウィンドウで Google アカウントにログインしてください。
ログイン状態はプロファイルに保存され、次回以降は不要です。

普段使いの Chrome は起動したままで構いません（プロファイルが別なので競合しません）。

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

`[KEEP]` に指定した各メモについて、以下を順に行います。

1. Keep で該当メモを検索し、「Google ドキュメントにコピー」を実行する
2. コピー完了通知の「開く」から新しいタブを開き、コピー先ドキュメントの URL を取得する
3. コピー先ドキュメントをテキスト形式でエクスポートして本文を取得する
4. 結合先ドキュメントを開き、末尾に本文を入力する
5. エクスポート結果を再取得し、追記がドライブに保存されたことを確認する
6. **保存を確認できた場合のみ**、コピーをゴミ箱へ移動する

すべてログイン済みブラウザのセッションで行うため、Google Cloud のアプリ審査
（`エラー 403: access_denied`）の影響を受けません。

## 定期実行（Windows タスクスケジューラ）

| 項目 | 設定値 |
| --- | --- |
| トリガー | 毎日 23:00 など |
| プログラム/スクリプト | `C:\Path\To\KeepDrive\run.bat` |
| 開始（オプション） | `C:\Path\To\KeepDrive\` |

「コンピューターを AC 電源で使用している場合のみタスクを開始する」のチェックは外してください。

デバッグポート付きの Chrome はアプリが自動起動するため、タスクスケジューラ側での準備は不要です
（専用プロファイルにログイン済みであることが前提）。

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
  操作しています。Keep や Google ドキュメントの UI 変更で動作しなくなる可能性があります。
- 画面上のラベル（`その他` / `Google ドキュメントにコピー` / `開く` / `ファイル` /
  `ゴミ箱に移動`）は `app/constants.py` にまとめてあります。表示言語や UI が変わった場合は
  ここを調整します。
