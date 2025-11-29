"""RSS feed collection service"""
import feedparser
import html
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from src.models import RSSSource, NotifiedArticle
from src.config.settings import settings

logger = logging.getLogger(__name__)


class RSSService:
    """RSS収集サービス"""

    def __init__(self, db: Session):
        self.db = db

    def get_active_sources(self) -> List[RSSSource]:
        """有効なRSS情報源を取得"""
        return self.db.query(RSSSource).filter(RSSSource.is_active == True).all()

    def fetch_feed(self, url: str) -> Optional[feedparser.FeedParserDict]:
        """
        指定されたURLからRSSフィードを取得

        Args:
            url: RSS Feed URL

        Returns:
            feedparser.FeedParserDict or None
        """
        try:
            feed = feedparser.parse(url)

            # フィードが正常に取得できたか確認
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {url}: {feed.bozo_exception}")

            return feed
        except Exception as e:
            logger.error(f"Error fetching feed from {url}: {str(e)}")
            return None

    def parse_articles(self, feed: feedparser.FeedParserDict, source_id: int) -> List[Dict]:
        """
        フィードから記事情報を抽出

        Args:
            feed: feedparser.FeedParserDict
            source_id: RSS情報源のID

        Returns:
            記事情報のリスト
        """
        articles = []

        for entry in feed.entries:
            # 記事URLを取得
            article_url = entry.get("link", "")
            if not article_url:
                continue

            # タイトルを取得
            title = entry.get("title", "No Title")

            # 公開日時を取得
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                except Exception as e:
                    logger.warning(f"Error parsing published date: {str(e)}")

            articles.append({
                "article_url": article_url,
                "title": title,
                "published_at": published_at,
                "source_id": source_id
            })

        return articles

    def is_article_notified(self, article_url: str) -> bool:
        """
        記事が既に通知済みかチェック

        Args:
            article_url: 記事URL

        Returns:
            通知済みの場合True
        """
        existing = self.db.query(NotifiedArticle).filter(
            NotifiedArticle.article_url == article_url
        ).first()
        return existing is not None

    def is_article_within_age_limit(self, published_at: Optional[datetime]) -> bool:
        """
        記事が期間制限内かチェック

        Args:
            published_at: 記事の公開日時

        Returns:
            期間内の場合True、公開日時が不明で許可設定の場合もTrue
        """
        # 公開日時が不明な場合
        if published_at is None:
            if settings.ALLOW_UNKNOWN_DATE:
                logger.debug("Article has no publish date, allowing due to ALLOW_UNKNOWN_DATE=true")
                return True
            else:
                logger.debug("Article has no publish date, rejecting due to ALLOW_UNKNOWN_DATE=false")
                return False

        # 期間制限をチェック
        age_limit_days = settings.ARTICLE_AGE_LIMIT_DAYS
        cutoff_date = datetime.now() - timedelta(days=age_limit_days)

        is_within_limit = published_at >= cutoff_date

        if not is_within_limit:
            logger.debug(
                f"Article published at {published_at} is older than {age_limit_days} days, skipping"
            )

        return is_within_limit

    def contains_excluded_keyword(self, title: str) -> bool:
        """
        タイトルに除外キーワードが含まれているかチェック

        Args:
            title: 記事タイトル

        Returns:
            除外キーワードが含まれている場合True
        """
        if not settings.ENABLE_KEYWORD_FILTER:
            return False

        # HTMLエンティティをデコード（例: &#038; → &）
        decoded_title = html.unescape(title)

        # 各除外キーワードをチェック（大文字小文字を区別しない）
        for keyword in settings.EXCLUDE_KEYWORDS:
            if keyword.lower() in decoded_title.lower():
                logger.info(f"Article excluded by keyword '{keyword}': {decoded_title[:80]}...")
                return True

        return False

    def get_new_articles(self) -> tuple[List[Dict], Dict]:
        """
        全RSS情報源から未通知の記事を取得

        Returns:
            (未通知記事のリスト, 統計情報)
            統計情報: {
                "total_sources": 監視中のRSS数,
                "successful_sources": 取得成功したRSS数,
                "errors": エラー情報のリスト
            }
        """
        new_articles = []
        sources = self.get_active_sources()
        errors = []
        successful_count = 0

        logger.info(f"Fetching articles from {len(sources)} RSS sources")

        for source in sources:
            try:
                logger.info(f"Fetching feed from: {source.name} ({source.url})")
                feed = self.fetch_feed(source.url)

                if not feed:
                    logger.warning(f"Failed to fetch feed from {source.name}")
                    errors.append({
                        "source_name": source.name,
                        "error": "フィード取得失敗"
                    })
                    continue

                if not feed.entries:
                    logger.warning(f"No entries found in feed from {source.name}")
                    errors.append({
                        "source_name": source.name,
                        "error": "記事なし"
                    })
                    continue

                successful_count += 1
                articles = self.parse_articles(feed, source.id)
                logger.info(f"Found {len(articles)} articles from {source.name}")

                # 未通知 & 期間内 & キーワード除外の記事をフィルタリング
                for article in articles:
                    # 未通知チェック
                    if self.is_article_notified(article["article_url"]):
                        continue

                    # 期間制限チェック
                    if not self.is_article_within_age_limit(article.get("published_at")):
                        continue

                    # 除外キーワードチェック
                    if self.contains_excluded_keyword(article.get("title", "")):
                        continue

                    # フィルタをパスした記事を追加
                    article["source_name"] = source.name
                    new_articles.append(article)

            except Exception as e:
                logger.error(f"Error processing source {source.name}: {str(e)}")
                errors.append({
                    "source_name": source.name,
                    "error": str(e)[:50]  # エラーメッセージを50文字に制限
                })
                continue

        logger.info(f"Total new articles found: {len(new_articles)}")

        stats = {
            "total_sources": len(sources),
            "successful_sources": successful_count,
            "errors": errors
        }

        return new_articles, stats

    def mark_as_notified(self, articles: List[Dict]) -> None:
        """
        記事を通知済みとしてDBに保存

        Args:
            articles: 記事情報のリスト
        """
        try:
            for article in articles:
                notified_article = NotifiedArticle(
                    article_url=article["article_url"],
                    title=article["title"],
                    published_at=article.get("published_at"),
                    source_id=article["source_id"]
                )
                self.db.add(notified_article)

            self.db.commit()
            logger.info(f"Marked {len(articles)} articles as notified")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking articles as notified: {str(e)}")
            raise
