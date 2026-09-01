import logging
import sys

from app.constants import (
    MSG_FATAL_ERROR,
    MSG_MEMO_MERGE_FAILED,
    MSG_MEMO_START,
    MSG_MERGE_COMPLETED,
    MSG_MERGE_START,
    MSG_NO_TARGET_MEMO,
)
from service.chrome_session import open_chrome_page
from service.keep_doc_merge import merge_memo
from utils.config_manager import get_merge_targets, load_config
from utils.log_rotation import setup_logging

logger = logging.getLogger(__name__)


def run() -> int:
    """対象メモをGoogleドキュメントへコピーし、結合先ドキュメントへ追記する。"""
    # 設定読み込みが失敗しても記録が残るよう、ログを先に初期化する
    setup_logging()
    logger.info(MSG_MERGE_START)

    targets = get_merge_targets(load_config())
    if not targets:
        logger.warning(MSG_NO_TARGET_MEMO)
        return 1

    failure_count = 0
    with open_chrome_page() as page:
        for current, (title, destination_url) in enumerate(targets.items(), start=1):
            logger.info(
                MSG_MEMO_START.format(
                    current=current, total=len(targets), title=title
                )
            )
            # 1件の失敗で残りのメモを止めない
            try:
                merge_memo(page, title, destination_url)
            except Exception as e:
                logger.error(MSG_MEMO_MERGE_FAILED.format(title=title, error=e))
                failure_count += 1

    logger.info(
        MSG_MERGE_COMPLETED.format(
            success=len(targets) - failure_count, failure=failure_count
        )
    )
    return 1 if failure_count else 0


def main() -> int:
    try:
        return run()
    except Exception as e:
        logger.error(MSG_FATAL_ERROR.format(error=e), exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
