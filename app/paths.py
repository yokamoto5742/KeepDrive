from pathlib import Path
from typing import Final

# 仕様書 §3: main.py が存在するディレクトリを基準パスとする
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent

CREDENTIALS_PATH: Final[Path] = BASE_DIR / 'credentials.json'
TOKEN_PATH: Final[Path] = BASE_DIR / 'token.json'
