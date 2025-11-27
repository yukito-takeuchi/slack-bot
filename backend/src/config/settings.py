"""Application configuration settings"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/slack_bot"
    )

    # Slack
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")

    # Notification
    NOTIFICATION_TIME: str = os.getenv("NOTIFICATION_TIME", "09:00")

    # Article filtering
    ARTICLE_AGE_LIMIT_DAYS: int = int(os.getenv("ARTICLE_AGE_LIMIT_DAYS", "7"))
    ALLOW_UNKNOWN_DATE: bool = os.getenv("ALLOW_UNKNOWN_DATE", "true").lower() == "true"

    # Timezone
    TIMEZONE: str = os.getenv("TZ", "Asia/Tokyo")

    # Application
    APP_NAME: str = "Slack Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


settings = Settings()
