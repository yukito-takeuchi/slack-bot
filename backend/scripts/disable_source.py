"""RSS情報源を無効化するスクリプト"""
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.database import SessionLocal
from src.models import RSSSource


def disable_source(source_name: str):
    """指定したRSS情報源を無効化"""
    db = SessionLocal()

    try:
        source = db.query(RSSSource).filter(RSSSource.name == source_name).first()

        if source:
            source.is_active = False
            db.commit()
            print(f"✅ '{source_name}' を無効化しました。")
        else:
            print(f"❌ '{source_name}' が見つかりませんでした。")

    except Exception as e:
        db.rollback()
        print(f"❌ エラーが発生しました: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python disable_source.py <source_name>")
        print("Example: python disable_source.py ZOZO")
        sys.exit(1)

    source_name = sys.argv[1]
    disable_source(source_name)
