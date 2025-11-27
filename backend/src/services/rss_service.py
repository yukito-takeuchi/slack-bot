"""RSS feed collection service"""
import feedparser
from datetime import datetime
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from src.models import RSSSource, NotifiedArticle

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

    def get_new_articles(self) -> List[Dict]:
        """
        全RSS情報源から未通知の記事を取得

        Returns:
            未通知記事のリスト
        """
        new_articles = []
        sources = self.get_active_sources()

        logger.info(f"Fetching articles from {len(sources)} RSS sources")

        for source in sources:
            try:
                logger.info(f"Fetching feed from: {source.name} ({source.url})")
                feed = self.fetch_feed(source.url)

                if not feed:
                    logger.warning(f"Failed to fetch feed from {source.name}")
                    continue

                articles = self.parse_articles(feed, source.id)
                logger.info(f"Found {len(articles)} articles from {source.name}")

                # 未通知の記事をフィルタリング
                for article in articles:
                    if not self.is_article_notified(article["article_url"]):
                        article["source_name"] = source.name
                        new_articles.append(article)

            except Exception as e:
                logger.error(f"Error processing source {source.name}: {str(e)}")
                continue

        logger.info(f"Total new articles found: {len(new_articles)}")
        return new_articles

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
