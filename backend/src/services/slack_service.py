"""Slack notification service"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from src.config.settings import settings

logger = logging.getLogger(__name__)


class SlackService:
    """Slack通知サービス"""

    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL

    def format_message(
        self,
        articles: List[Dict],
        total_sources: int = 0,
        successful_sources: int = 0,
        errors: Optional[List[Dict]] = None
    ) -> str:
        """
        記事リストをSlackメッセージ形式に整形

        Args:
            articles: 記事情報のリスト
            total_sources: 監視中の総RSS数
            successful_sources: 取得成功したRSS数
            errors: エラー情報のリスト

        Returns:
            整形されたメッセージ
        """
        # ヘッダー
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"【本日の技術ブログ更新】{today}\n\n"

        # 記事情報
        if not articles:
            message += "本日の新着記事はありません\n\n"
        else:
            message += f"✅ 新着記事: {len(articles)}件\n\n"

            # 記事リスト
            for article in articles:
                title = article.get("title", "No Title")
                url = article.get("article_url", "")
                source_name = article.get("source_name", "Unknown")
                published_at = article.get("published_at")

                # 公開日時の整形
                date_str = ""
                if published_at:
                    if isinstance(published_at, str):
                        date_str = published_at
                    elif isinstance(published_at, datetime):
                        date_str = published_at.strftime('%Y-%m-%d')

                message += f"[{source_name}] {title}\n"
                message += f"{url}\n"
                if date_str:
                    message += f"公開日: {date_str}\n"
                message += "\n"

        # エラー情報
        if errors and len(errors) > 0:
            message += f"⚠️ 取得エラー: {len(errors)}サイト\n"
            for error in errors[:5]:  # 最大5件まで表示
                source_name = error.get("source_name", "Unknown")
                error_msg = error.get("error", "Unknown error")
                message += f"- {source_name} ({error_msg})\n"

            if len(errors) > 5:
                message += f"...他 {len(errors) - 5}件\n"
            message += "\n"

        # 統計情報
        if total_sources > 0:
            message += f"📊 監視中: {total_sources}サイト | 今日の取得成功: {successful_sources}サイト\n"

        return message

    def send_notification(
        self,
        articles: List[Dict],
        total_sources: int = 0,
        successful_sources: int = 0,
        errors: Optional[List[Dict]] = None
    ) -> bool:
        """
        Slackに通知を送信

        Args:
            articles: 記事情報のリスト
            total_sources: 監視中の総RSS数
            successful_sources: 取得成功したRSS数
            errors: エラー情報のリスト

        Returns:
            成功した場合True、失敗した場合False
        """
        if not self.webhook_url:
            logger.error("SLACK_WEBHOOK_URL is not configured")
            return False

        try:
            message = self.format_message(
                articles=articles,
                total_sources=total_sources,
                successful_sources=successful_sources,
                errors=errors
            )

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
