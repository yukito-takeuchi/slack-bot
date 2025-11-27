"""Slack notification service"""
import requests
import logging
from typing import List, Dict
from datetime import datetime
from src.config.settings import settings

logger = logging.getLogger(__name__)


class SlackService:
    """Slack通知サービス"""

    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL

    def format_message(self, articles: List[Dict]) -> str:
        """
        記事リストをSlackメッセージ形式に整形

        Args:
            articles: 記事情報のリスト

        Returns:
            整形されたメッセージ
        """
        if not articles:
            return "本日は新着記事がありませんでした。"

        # ヘッダー
        today = datetime.now().strftime("%Y年%m月%d日")
        message = f":newspaper: *技術ブログ新着記事* ({today})\n\n"
        message += f"本日は *{len(articles)}件* の新着記事があります！\n\n"

        # 記事リスト
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No Title")
            url = article.get("article_url", "")
            source_name = article.get("source_name", "Unknown")
            published_at = article.get("published_at")

            # 公開日時の整形
            date_str = ""
            if published_at:
                if isinstance(published_at, str):
                    date_str = f" | {published_at}"
                elif isinstance(published_at, datetime):
                    date_str = f" | {published_at.strftime('%Y-%m-%d')}"

            message += f"{i}. *<{url}|{title}>*\n"
            message += f"   :office: {source_name}{date_str}\n\n"

        message += "\n_良い一日を！_ :coffee:"

        return message

    def send_notification(self, articles: List[Dict]) -> bool:
        """
        Slackに通知を送信

        Args:
            articles: 記事情報のリスト

        Returns:
            成功した場合True、失敗した場合False
        """
        if not self.webhook_url:
            logger.error("SLACK_WEBHOOK_URL is not configured")
            return False

        try:
            message = self.format_message(articles)

            payload = {
                "text": message,
                "username": "Tech Blog Bot",
                "icon_emoji": ":robot_face:"
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Successfully sent notification with {len(articles)} articles")
                return True
            else:
                logger.error(f"Failed to send notification. Status code: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            logger.error("Timeout while sending notification to Slack")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending notification to Slack: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in send_notification: {str(e)}")
            return False

    def send_test_notification(self) -> bool:
        """
        テスト通知を送信

        Returns:
            成功した場合True、失敗した場合False
        """
        test_articles = [
            {
                "title": "テスト記事：Slack Bot が正常に動作しています",
                "article_url": "https://example.com/test",
                "source_name": "Tech Blog Bot",
                "published_at": datetime.now()
            }
        ]

        return self.send_notification(test_articles)
