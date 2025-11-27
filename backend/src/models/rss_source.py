"""RSS Source model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from src.config.database import Base


class RSSSource(Base):
    """RSS情報源を管理するモデル"""
    __tablename__ = "rss_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="企業名・サイト名")
    url = Column(Text, nullable=False, unique=True, comment="RSS Feed URL")
    is_active = Column(Boolean, default=True, nullable=False, comment="有効/無効")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RSSSource(id={self.id}, name='{self.name}', is_active={self.is_active})>"
