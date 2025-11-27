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
        2. Slackに通知
        3. 通知済みとしてDBに保存

        Returns:
            成功した場合True、失敗した場合False
        """
        try:
            logger.info("Starting notification process")

            # 1. 新着記事を取得
            new_articles = self.rss_service.get_new_articles()

            if not new_articles:
                logger.info("No new articles found")
                # 新着記事がない場合もSlackに通知（オプション）
                # self.slack_service.send_notification([])
                return True

            logger.info(f"Found {len(new_articles)} new articles")

            # 2. Slackに通知
            notification_sent = self.slack_service.send_notification(new_articles)

            if not notification_sent:
                logger.error("Failed to send notification to Slack")
                return False

            # 3. 通知済みとして保存
            self.rss_service.mark_as_notified(new_articles)

            logger.info("Notification process completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error in notification process: {str(e)}", exc_info=True)
            return False
