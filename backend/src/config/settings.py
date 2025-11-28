"""Application configuration settings"""
import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """
    DATABASE_URLを取得
    Herokuの古い形式（postgres://）をpostgresql://に変換
    """
    url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/slack_bot"
    )
    # Herokuの古い形式を新しい形式に変換
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Settings:
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = get_database_url()

    # Slack
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")

    # Notification
    NOTIFICATION_TIME: str = os.getenv("NOTIFICATION_TIME", "09:00")

    # Article filtering
    ARTICLE_AGE_LIMIT_DAYS: int = int(os.getenv("ARTICLE_AGE_LIMIT_DAYS", "7"))
    ALLOW_UNKNOWN_DATE: bool = os.getenv("ALLOW_UNKNOWN_DATE", "true").lower() == "true"

    # Keyword filtering
    ENABLE_KEYWORD_FILTER: bool = os.getenv("ENABLE_KEYWORD_FILTER", "true").lower() == "true"
    EXCLUDE_KEYWORDS: List[str] = [
        kw.strip() for kw in os.getenv("EXCLUDE_KEYWORDS", "開催,お知らせ,募集,採用,Advent Calendar").split(",")
    ]

    # Timezone
    TIMEZONE: str = os.getenv("TZ", "Asia/Tokyo")

    # Application
    APP_NAME: str = "Slack Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


settings = Settings()
