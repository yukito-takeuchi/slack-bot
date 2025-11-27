"""Job scheduler for periodic tasks"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from src.config.settings import settings
from src.config.database import SessionLocal
from src.services import NotificationService

logger = logging.getLogger(__name__)


class JobScheduler:
    """定期実行ジョブのスケジューラー"""

    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone=pytz.timezone(settings.TIMEZONE)
        )

    def notification_job(self):
        """通知ジョブ（スケジューラーから呼び出される）"""
        logger.info("Running scheduled notification job")

        db = SessionLocal()
        try:
            service = NotificationService(db)
            success = service.run()

            if success:
                logger.info("Scheduled notification job completed successfully")
            else:
                logger.error("Scheduled notification job failed")

        except Exception as e:
            logger.error(f"Error in notification job: {str(e)}", exc_info=True)
        finally:
            db.close()

    def start(self):
        """スケジューラーを起動"""
        # 通知時刻を取得（例: "09:00"）
        notification_time = settings.NOTIFICATION_TIME
        hour, minute = notification_time.split(":")

        # Cronトリガーを設定（毎日指定時刻に実行）
        trigger = CronTrigger(
            hour=int(hour),
            minute=int(minute),
            timezone=settings.TIMEZONE
        )

        # ジョブを追加
        self.scheduler.add_job(
            self.notification_job,
            trigger=trigger,
            id="daily_notification",
            name="Daily Tech Blog Notification",
            replace_existing=True
        )

        # スケジューラーを開始
        self.scheduler.start()
        logger.info(
            f"Scheduler started. Notification job will run daily at {notification_time} {settings.TIMEZONE}"
        )

    def stop(self):
        """スケジューラーを停止"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def run_immediately(self):
        """即座にジョブを実行（テスト用）"""
        logger.info("Running notification job immediately")
        self.notification_job()


# グローバルスケジューラーインスタンス
scheduler = JobScheduler()
