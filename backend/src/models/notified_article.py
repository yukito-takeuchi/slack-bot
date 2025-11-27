"""Notified Article model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import Base


class NotifiedArticle(Base):
    """通知済み記事を管理するモデル"""
    __tablename__ = "notified_articles"

    id = Column(Integer, primary_key=True, index=True)
    article_url = Column(Text, nullable=False, unique=True, index=True, comment="記事URL")
    title = Column(Text, comment="記事タイトル")
    published_at = Column(DateTime, comment="公開日時")
    notified_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="通知日時")
    source_id = Column(Integer, ForeignKey("rss_sources.id"), comment="情報源ID")

    # Relationship
    source = relationship("RSSSource", backref="notified_articles")

    def __repr__(self):
        return f"<NotifiedArticle(id={self.id}, title='{self.title}', url='{self.article_url[:50]}...')>"
