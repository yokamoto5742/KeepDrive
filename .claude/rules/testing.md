---
description: テスト実行コマンドとテスト方針
---

## テスト実行コマンド

```bash
# 全件
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

# 単一ファイル
.venv\Scripts\python.exe -m pytest tests/service/test_sync_service.py -v

# 単一テスト
.venv\Scripts\python.exe -m pytest tests/service/test_sync_service.py::test_sort_items_orders_by_updated_desc -v

# カバレッジ付き
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short --cov=app --cov-report=html
```
