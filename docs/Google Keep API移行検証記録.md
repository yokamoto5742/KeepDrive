# 公式 Google Keep API への移行検証記録（断念）

- **検証日:** 2026-08-27
- **対象アカウント:** 個人アカウント（`@gmail.com`）
- **結論:** **移行不可能。本方針は断念する。**

---

## 1. 目的

KeepDrive は Google Keep へのアクセスに非公式ライブラリ `gkeepapi` を使用している。
`gkeepapi` は Google の内部 API を利用しており、以下のリスクを抱えている。

- Google 側の仕様変更で予告なく動作しなくなる
- ログインにマスタートークン（`gpsoauth` 経由で取得）が必要で、取得手順が煩雑
- マスタートークンはアカウント全体への強い権限を持つため、漏洩時の影響が大きい

これを解消するため、公式の Google Keep API（`keep.googleapis.com` v1）へ
全面的に書き換えることを検討した。

---

## 2. 検証内容

GCP コンソールで Google Keep API を有効化した上で、`scripts/probe_keep_api.py` により
以下の3点を順に確認する計画とした。

| 手順 | 内容 | 結果 |
|---|---|---|
| 1 | `auth/keep` スコープで OAuth 同意を通せるか | **失敗** |
| 2 | `notes.list` でメモを取得できるか | 未到達 |
| 3 | `notes.create` で空リストメモを作成できるか | 未到達 |

### 手順1の結果（実際のエラー）

```
アクセスをブロック: 認証エラーです

yokamoto5742@gmail.com
Some requested scopes cannot be shown: [https://www.googleapis.com/auth/keep]
KeepDrive のデベロッパーの場合は、エラーの詳細をご確認ください。
エラー 400: invalid_scope
```

OAuth 同意画面に到達した時点で拒否されるため、API を1回も呼び出せない。

---

## 3. 失敗の原因

### 3.1 直接原因: consumer アカウントには `auth/keep` スコープが発行されない

`invalid_scope` は「同意画面のスコープ設定漏れ」ではなく、**Google が個人アカウントに対して
`https://www.googleapis.com/auth/keep` スコープの発行自体を拒否している**ことを意味する。

Google Keep API は「エンタープライズ管理者が CASB（Cloud Access Security Broker）で
検出した問題を解決する」ための管理系 API として設計されており、
**Google Workspace（Business / Enterprise / Education 各エディション）専用**である。

### 3.2 「API を有効化した」だけでは解決しない理由

GCP コンソールでの API 有効化は「この GCP プロジェクトからこの API を呼ぶことを許可する」
という設定にすぎず、**呼び出し元アカウントの種別による制限とは別のレイヤー**にある。
そのため有効化は成功するが、OAuth の段階で弾かれる。

以下を試しても解消しない。

- OAuth 同意画面に `auth/keep` スコープを追加する
- 同意画面を「テスト」から「本番」に変更する
- 別の OAuth クライアント ID を作り直す

---

## 4. 副次的に判明した制約

仮に Google Workspace アカウントへ移行して手順1を突破できたとしても、
公式 API の仕様上、**現行仕様の一部は実装できない**ことが判明した。
（`google-api-python-client` 同梱の discovery ドキュメント `keep.v1.json` を実際に読んで確認）

### 4.1 提供メソッドが4つしかない

```
notes.create  POST   v1/notes
notes.get     GET    v1/{+name}
notes.list    GET    v1/notes        （filter, pageSize, pageToken）
notes.delete  DELETE v1/{+name}
```

その他に `media.download`、`notes.permissions.batchCreate` / `batchDelete` があるのみ。

### 4.2 現行仕様への影響

| 現行仕様 | 公式 API での可否 |
|---|---|
| §5-4-e メモ内のアイテムを全削除して空にする | **不可**。`update` / `patch` が存在せず既存メモを編集できない。`delete`（完全削除・復元不可）→ 同名で空リストを `create` する代替しかなく、メモ ID・色・ピン留め・ラベル・リマインダーが失われる |
| §6.1 アイテム更新日時の降順ソート | **不可**。`ListItem` のフィールドは `text` / `checked` / `childListItems` のみで、アイテム単位のタイムスタンプが存在しない |
| アーカイブ済みメモの除外 | **不可**。Note リソースに `archived` フィールドが無い（`trashed` のみ） |

つまり公式 API は「Keep の管理・棚卸し」用であり、
**本アプリのような日常的なメモ操作の自動化には機能が不足している**。

---

## 5. 検討した代替案

| 案 | 内容 | 評価 |
|---|---|---|
| A | `gkeepapi` を継続し、トークン失効検知やリトライで堅牢化する | 変更は最小だが非公式依存は残る |
| B | 入力先を Google ToDo（Tasks API）へ移行する | Tasks API は個人アカウントで公式サポートされ、一覧取得・個別削除がすべて可能。非公式依存を完全に排除できる唯一の案。ただし日々の入力先アプリが変わる |
| C | Google Workspace（独自ドメイン + Business Standard 以上）を契約する | 月額費用が発生し、既存メモの移行も必要。さらに §4.2 の制約は残るため費用対効果が低い |

いずれも採用せず、**今回は本プロジェクト（公式 API への移行）自体を断念する**。

---

## 6. 再検討する場合のトリガー

以下のいずれかが起きた場合に限り、再検討の価値がある。

- Google Issue Tracker [263769283](https://issuetracker.google.com/issues/263769283)
  （非エンタープライズアカウントへの Keep API 開放要望）が実装される
- Keep API に `notes.update` / `notes.patch` が追加される
  （[リリースノート](https://developers.google.com/workspace/keep/release-notes) を参照）
- Google Workspace アカウントへ移行する事情が別途生じる

---

## 7. 残置物

- `scripts/probe_keep_api.py` — 本検証に使用したスクリプト。上記トリガー発生時の再検証に
  そのまま使える。不要であれば削除してよい
- `.gitignore` の `token_keep_probe.json` — 同スクリプト用の除外設定
- 検証用トークンファイルは認証成功前に拒否されたため生成されていない

---

## 8. 参考資料

- [Google Keep API リファレンス](https://developers.google.com/workspace/keep/api/reference/rest)
- [Method: notes.list](https://developers.google.com/workspace/keep/api/reference/rest/v1/notes/list)
- [Google Keep API 概要](https://developers.google.com/workspace/keep/api/guides)
- [Issue 263769283: Google Keep API for Non-Enterprise Accounts](https://issuetracker.google.com/issues/263769283)
