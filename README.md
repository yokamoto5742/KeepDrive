# KeepDrive

Google Keep のリストメモを Google ドライブ内の同名フォルダ配下の Google ドキュメントへ
1日1回追記し、元の Keep メモを空にする Windows 向けバッチツールです。

取り込むリスト名を設定ファイルで指定でき、指定したリストだけを処理できます。

## 動作環境

- Windows 11 / Python 3.13 以上
- プロジェクト配下の仮想環境（`.venv`）

## セットアップ

### 1. 依存パッケージのインストール

```bash
uv sync
```

### 2. Google Keep のマスタートークンを取得する

`gkeepapi` はアプリパスワードでログインできないため、マスタートークンが必要です。

```bash
.venv\Scripts\python.exe scripts\get_keep_token.py
```

画面の案内に従って以下を行います。

1. シークレットウィンドウで <https://accounts.google.com/EmbeddedSetup> を開く
2. Google アカウントでログインし（2段階認証も完了させる）、「同意する」をクリック
3. 開発者ツール（F12）→ Application → Cookies から `oauth_token` の値をコピー
4. スクリプトにメールアドレスと `oauth_token` を入力

出力された内容をプロジェクトルートの `.env` に貼り付けます。

```
KEEP_EMAIL=your-account@gmail.com
KEEP_MASTER_TOKEN=aas_et/...
```

### 3. Drive / Docs API の認証情報を配置する

1. Google Cloud コンソールで Drive API と Docs API を有効化する
2. 「OAuth クライアント ID」を**デスクトップアプリ**として作成する
3. ダウンロードした JSON を `credentials.json` としてプロジェクトルートに置く

初回実行時のみブラウザが開いて認証を求められ、成功すると `token.json` が生成されます。
以降は `token.json` が再利用されるため、ブラウザ認証は不要です。

### 4. 取り込むリスト名を指定する

`utils/config.ini` の `[KEEP]` セクションを編集します。

```ini
[KEEP]
# 取り込むリスト名をカンマ区切りで指定する。空欄の場合は全リストを対象にする
target_lists = 読書,ショッピング,生活
```

- 空欄にすると Keep 上のすべてのリストメモが対象になります
- ここに書かれていないリストは一切変更されません
- 指定した名前が Keep 上に見つからない場合は警告としてログに記録されます

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

1. Keep 内のリストメモを走査し、タイトルがありアイテムが1件以上あるものを抽出
2. `target_lists` で対象を絞り込む
3. 各メモについて
   1. アイテムを更新日時の降順（同時刻はテキスト昇順）に並べ替える
   2. ドライブ内の同名フォルダを検索（無ければマイドライブ直下に作成）
   3. フォルダ内の同名ドキュメントを検索（無ければ作成）
   4. ドキュメント末尾にアイテム名のみを1行ずつ追記する
   5. **追記が成功した場合のみ** Keep メモのアイテムを全削除する
4. Keep の変更をリモートへ同期する

追記フォーマットはアイテム名のみで、チェックボックスや日付見出しは付きません。

## 定期実行（Windows タスクスケジューラ）

| 項目 | 設定値 |
| --- | --- |
| トリガー | 毎日 23:00 など |
| プログラム/スクリプト | `C:\Path\To\KeepDrive\run.bat` |
| 開始（オプション） | `C:\Path\To\KeepDrive\` |

「コンピューターを AC 電源で使用している場合のみタスクを開始する」のチェックは外してください。

バックグラウンド実行にする場合は `.venv\Scripts\pythonw.exe` に引数 `main.py` を指定します。

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

- Google Keep には個人アカウント（`@gmail.com`）向けの公式 API がなく、非公式クライアント
  `gkeepapi` を利用しています。Google 側の仕様変更で動作しなくなる可能性があります。
- `.env` / `credentials.json` / `token.json` / `.gkeep_token` は Git 管理対象外です。
