"""Main notification service that orchestrates RSS collection and Slack notification"""
import logging
from sqlalchemy.orm import Session
from .rss_service import RSSService
from .slack_service import SlackService

logger = logging.getLogger(__name__)


class NotificationService:
    """通知処理を統括するサービス"""

    def __init__(self, db: Session):
        self.db = db
        self.rss_service = RSSService(db)
        self.slack_service = SlackService()

    def run(self) -> bool:
        """
        メイン処理フロー:
        1. RSS巡回して新着記事を取得
        2. Slackに通知（記事0件でも通知）
        3. 通知済みとしてDBに保存

        Returns:
            成功した場合True、失敗した場合False
        """
        try:
            logger.info("Starting notification process")

            # 1. 新着記事と統計情報を取得
            new_articles, stats = self.rss_service.get_new_articles()

            total_sources = stats.get("total_sources", 0)
            successful_sources = stats.get("successful_sources", 0)
            errors = stats.get("errors", [])

            logger.info(
                f"RSS collection completed: "
                f"{len(new_articles)} new articles, "
                f"{successful_sources}/{total_sources} sources succeeded, "
                f"{len(errors)} errors"
            )

            # 2. Slackに通知（記事0件でも必ず通知）
            notification_sent = self.slack_service.send_notification(
                articles=new_articles,
                total_sources=total_sources,
                successful_sources=successful_sources,
                errors=errors
            )

            if not notification_sent:
                logger.error("Failed to send notification to Slack")
                return False

            # 3. 通知済みとして保存（記事がある場合のみ）
            if new_articles:
                self.rss_service.mark_as_notified(new_articles)

            logger.info("Notification process completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error in notification process: {str(e)}", exc_info=True)
            return False
