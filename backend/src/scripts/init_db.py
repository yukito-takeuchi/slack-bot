"""Heroku release phase用のデータベース初期化スクリプト"""
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.config.database import init_db

def main():
    """データベーステーブルを初期化"""
    print("Initializing database tables...")
    try:
        init_db()
        print("✅ Database tables initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
