"""Main FastAPI application entry point"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.config.database import get_db, init_db
from src.scheduler import scheduler

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時の処理
    logger.info("Application startup")

    # データベース初期化
    init_db()
    logger.info("Database initialized")

    # スケジューラー起動
    scheduler.start()
    logger.info("Scheduler started")

    yield

    # 終了時の処理
    logger.info("Application shutdown")
    scheduler.stop()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="Slack Bot API",
    description="RSS feed aggregator and Slack notification bot",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Slack Bot API is running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "slack-bot",
        "version": "1.0.0"
    }


@app.post("/trigger-notification")
async def trigger_notification(db: Session = Depends(get_db)):
    """
    手動で通知を実行するエンドポイント（テスト用）
    """
    from src.services import NotificationService

    try:
        service = NotificationService(db)
        success = service.run()

        if success:
            return {
                "status": "success",
                "message": "Notification sent successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to send notification"
            }
    except Exception as e:
        logger.error(f"Error triggering notification: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/sources")
async def get_sources(db: Session = Depends(get_db)):
    """登録されているRSS情報源の一覧を取得"""
    from src.models import RSSSource

    sources = db.query(RSSSource).all()
    return {
        "count": len(sources),
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "url": s.url,
                "is_active": s.is_active,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in sources
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
