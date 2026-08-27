import logging
import sys

from app.constants import (
    MSG_FATAL_ERROR,
    MSG_NO_TARGET_NOTES,
    MSG_SYNC_COMPLETED,
    MSG_SYNC_START,
)
from service.google_auth import build_docs_service, build_drive_service, load_credentials
from service.keep_client import authenticate_keep, fetch_list_notes, save_state
from service.sync_service import filter_target_notes, sync_notes
from utils.config_manager import get_target_list_names, load_config
from utils.env_loader import load_environment_variables
from utils.log_rotation import setup_logging

logger = logging.getLogger(__name__)


def run() -> int:
    """仕様書 §5 の処理フローを実行し、終了コードを返す。"""
    load_environment_variables()
    config = load_config()
    setup_logging(config)
    logger.info(MSG_SYNC_START)

    keep = authenticate_keep()
    credentials = load_credentials()
    drive = build_drive_service(credentials)
    docs = build_docs_service(credentials)

    notes = filter_target_notes(
        fetch_list_notes(keep), get_target_list_names(config)
    )
    if not notes:
        logger.info(MSG_NO_TARGET_NOTES)
        return 0

    result = sync_notes(notes, drive, docs)

    keep.sync()
    save_state(keep)

    logger.info(
        MSG_SYNC_COMPLETED.format(
            success=result.success_count, failure=result.failure_count
        )
    )
    return 1 if result.failure_count else 0


def main() -> int:
    try:
        return run()
    except Exception as e:
        logging.error(MSG_FATAL_ERROR.format(error=e), exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
