"""初期データ投入スクリプト - 日本企業の技術ブログRSSを登録"""
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.database import SessionLocal, init_db
from src.models import RSSSource


def init_rss_sources():
    """日本企業の技術ブログRSSを初期登録"""

    # データベース初期化
    init_db()

    # RSS情報源のリスト
    sources = [
        {
            "name": "メルカリ",
            "url": "https://engineering.mercari.com/blog"
        },
        {
            "name": "サイバーエージェント",
            "url": "https://developers.cyberagent.co.jp/blog/"
        },
        {
            "name": "LINE",
            "url": "https://engineering.linecorp.com/ja/blog/"
        },
        {
            "name": "楽天",
            "url": "https://tech.rakuten.co.jp/"
        },
        {
            "name": "DeNA",
            "url": "https://engineering.dena.com/blog/"
        },
        {
            "name": "クックパッド",
            "url": "https://techlife.cookpad.com"
        },
        {
            "name": "ヤフー",
            "url": "https://techblog.yahoo.co.jp/"
        },
        {
            "name": "リクルート",
            "url": "https://engineer.recruit-lifestyle.co.jp/techblog/"
        },
        {
            "name": "はてな",
            "url": "https://developer.hatenastaff.com"
        },
        {
            "name": "ミクシィ",
            "url": "https://mixi-developers.mixi.co.jp"
        },
        {
            "name": "GMOペパボ",
            "url": "https://tech.pepabo.com"
        },
        {
            "name": "ZOZO",
            "url": "https://techblog.zozo.com"
        },
    ]

    db = SessionLocal()

    try:
        # 既存データをチェック
        existing_count = db.query(RSSSource).count()

        if existing_count > 0:
            print(f"既に {existing_count} 件のRSS情報源が登録されています。")
            response = input("既存データを削除して再登録しますか？ (y/N): ")

            if response.lower() == 'y':
                db.query(RSSSource).delete()
                db.commit()
                print("既存データを削除しました。")
            else:
                print("処理を中止します。")
                return

        # データ投入
        for source_data in sources:
            source = RSSSource(**source_data)
            db.add(source)

        db.commit()
        print(f"\n✅ {len(sources)} 件のRSS情報源を登録しました。\n")

        # 登録結果を表示
        all_sources = db.query(RSSSource).all()
        print("登録されたRSS情報源:")
        print("-" * 60)
        for s in all_sources:
            print(f"[{s.id}] {s.name}")
            print(f"    {s.url}")
            print(f"    有効: {s.is_active}")
            print()

    except Exception as e:
        db.rollback()
        print(f"❌ エラーが発生しました: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("初期データ投入スクリプト - 日本企業技術ブログRSS")
    print("=" * 60)
    print()

    init_rss_sources()

    print("=" * 60)
    print("完了しました！")
    print("=" * 60)
