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
        self.bot_token = settings.SLACK_BOT_TOKEN
        self.channel_id = settings.SLACK_CHANNEL_ID

    def format_main_message(
        self,
        article_count: int,
        total_sources: int = 0,
        successful_sources: int = 0,
        error_count: int = 0
    ) -> str:
        """
        メイン投稿メッセージを整形（スレッド親）

        Args:
            article_count: 新着記事数
            total_sources: 監視中の総RSS数
            successful_sources: 取得成功したRSS数
            error_count: エラー数

        Returns:
            整形されたメッセージ
        """
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"📰 【本日の技術ブログ更新】{today}\n\n"

        if article_count == 0:
            message += "本日の新着記事はありません\n\n"
        else:
            message += f"✅ 新着記事: {article_count}件\n"
            if error_count > 0:
                message += f"⚠️ 取得エラー: {error_count}サイト\n"
            message += "\n"

        if total_sources > 0:
            message += f"📊 監視中: {total_sources}サイト | 取得成功: {successful_sources}サイト\n"

        if article_count > 0 or error_count > 0:
            message += "\n💬 詳細はスレッドで確認 →"

        return message

    def format_thread_articles(self, articles: List[Dict]) -> str:
        """
        スレッド内の記事一覧メッセージを整形

        Args:
            articles: 記事情報のリスト

        Returns:
            整形されたメッセージ
        """
        if not articles:
            return ""

        message = "📄 新着記事一覧\n\n"

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

        return message

    def format_thread_errors(self, errors: List[Dict]) -> str:
        """
        スレッド内のエラー情報メッセージを整形

        Args:
            errors: エラー情報のリスト

        Returns:
            整形されたメッセージ
        """
        if not errors:
            return ""

        message = "⚠️ 取得エラー詳細\n\n"

        for error in errors[:10]:  # 最大10件まで表示
            source_name = error.get("source_name", "Unknown")
            error_msg = error.get("error", "Unknown error")
            message += f"- {source_name} ({error_msg})\n"

        if len(errors) > 10:
            message += f"\n...他 {len(errors) - 10}件のエラー"

        return message

    def post_message(self, text: str, thread_ts: Optional[str] = None) -> Optional[str]:
        """
        Slack chat.postMessage APIでメッセージを送信

        Args:
            text: メッセージ本文
            thread_ts: スレッドのタイムスタンプ（スレッド返信の場合）

        Returns:
            投稿したメッセージのタイムスタンプ、失敗した場合None
        """
        if not self.bot_token or not self.channel_id:
            logger.error("SLACK_BOT_TOKEN or SLACK_CHANNEL_ID is not configured")
            return None

        try:
            url = "https://slack.com/api/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "channel": self.channel_id,
                "text": text,
                "username": "Tech Blog Bot",
                "icon_emoji": ":robot_face:"
            }

            if thread_ts:
                payload["thread_ts"] = thread_ts

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            result = response.json()

            if result.get("ok"):
                ts = result.get("ts")
                logger.info(f"Successfully posted message, ts: {ts}")
                return ts
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Failed to post message: {error}")
                return None

        except requests.exceptions.Timeout:
            logger.error("Timeout while posting message to Slack")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting message to Slack: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in post_message: {str(e)}")
            return None

    def send_notification(
        self,
        articles: List[Dict],
        total_sources: int = 0,
        successful_sources: int = 0,
        errors: Optional[List[Dict]] = None
    ) -> bool:
        """
        Slackに通知を送信（メイン投稿 + スレッド返信）

        Args:
            articles: 記事情報のリスト
            total_sources: 監視中の総RSS数
            successful_sources: 取得成功したRSS数
            errors: エラー情報のリスト

        Returns:
            成功した場合True、失敗した場合False
        """
        try:
            error_count = len(errors) if errors else 0

            # 1. メイン投稿を送信
            main_message = self.format_main_message(
                article_count=len(articles),
                total_sources=total_sources,
                successful_sources=successful_sources,
                error_count=error_count
            )

            thread_ts = self.post_message(main_message)

            if not thread_ts:
                logger.error("Failed to send main notification")
                return False

            logger.info(f"Successfully sent main notification, thread_ts: {thread_ts}")

            # 2. 記事がある場合、スレッドに記事一覧を投稿
            if articles:
                article_message = self.format_thread_articles(articles)
                if article_message:
                    article_ts = self.post_message(article_message, thread_ts=thread_ts)
                    if article_ts:
                        logger.info(f"Successfully posted {len(articles)} articles to thread")
                    else:
                        logger.warning("Failed to post articles to thread")

            # 3. エラーがある場合、スレッドにエラー情報を投稿
            if errors:
                error_message = self.format_thread_errors(errors)
                if error_message:
                    error_ts = self.post_message(error_message, thread_ts=thread_ts)
                    if error_ts:
                        logger.info(f"Successfully posted {len(errors)} errors to thread")
                    else:
                        logger.warning("Failed to post errors to thread")

            return True

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
