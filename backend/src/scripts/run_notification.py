"""Heroku Scheduler用の通知実行スクリプト"""
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.config.database import SessionLocal
from src.services import NotificationService
import logging

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """通知処理を実行"""
    logger.info("Starting notification job from Heroku Scheduler")

    db = SessionLocal()
    try:
        service = NotificationService(db)
        success = service.run()

        if success:
            logger.info("✅ Notification job completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Notification job failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error in notification job: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
