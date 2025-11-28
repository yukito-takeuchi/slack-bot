"""初期データ投入スクリプト - 日本企業の技術ブログRSSを登録"""
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.database import SessionLocal, init_db
from src.models import RSSSource, NotifiedArticle


def init_rss_sources():
    """日本企業の技術ブログRSSを初期登録"""

    # データベース初期化
    init_db()

    # RSS情報源のリスト（正しいRSS Feed URL）
    sources = [
        # 既存（12件）
        {
            "name": "メルカリ",
            "url": "https://engineering.mercari.com/blog/feed.xml"
        },
        {
            "name": "サイバーエージェント",
            "url": "https://developers.cyberagent.co.jp/blog/feed/"
        },
        {
            "name": "LINE",
            "url": "https://engineering.linecorp.com/ja/blog/rss"
        },
        {
            "name": "楽天",
            "url": "https://tech.rakuten.co.jp/feed/"
        },
        {
            "name": "DeNA",
            "url": "https://engineering.dena.com/blog/feed/"
        },
        {
            "name": "クックパッド",
            "url": "https://techlife.cookpad.com/feed"
        },
        {
            "name": "ヤフー",
            "url": "https://techblog.yahoo.co.jp/feed/"
        },
        {
            "name": "リクルート",
            "url": "https://engineer.recruit-lifestyle.co.jp/techblog/feed/"
        },
        {
            "name": "はてな",
            "url": "https://developer.hatenastaff.com/rss"
        },
        {
            "name": "ミクシィ",
            "url": "https://mixi-developers.mixi.co.jp/feed"
        },
        {
            "name": "GMOペパボ",
            "url": "https://tech.pepabo.com/feed.xml"
        },
        {
            "name": "ZOZO",
            "url": "https://techblog.zozo.com/rss.xml"
        },

        # 追加（18件）- 更新頻度が高い日本企業
        {
            "name": "Sansan",
            "url": "https://buildersbox.corp-sansan.com/rss.xml"
        },
        {
            "name": "SmartNews",
            "url": "https://developer.smartnews.com/blog/feed/"
        },
        {
            "name": "Retty",
            "url": "https://engineer.retty.me/feed"
        },
        {
            "name": "ドワンゴ",
            "url": "https://dwango.github.io/articles/feed.xml"
        },
        {
            "name": "カオナビ",
            "url": "https://techblog.kaonavi.jp/rss.xml"
        },
        {
            "name": "Chatwork",
            "url": "https://creators-note.chatwork.com/rss"
        },
        {
            "name": "eureka",
            "url": "https://medium.com/feed/eureka-engineering"
        },
        {
            "name": "freee",
            "url": "https://developers.freee.co.jp/feed"
        },
        {
            "name": "GREE",
            "url": "https://labs.gree.jp/blog/feed/"
        },
        {
            "name": "Gunosy",
            "url": "https://tech.gunosy.io/rss"
        },
        {
            "name": "Indeed",
            "url": "https://indeed-engineering.hatenablog.jp/rss"
        },
        {
            "name": "Ubie",
            "url": "https://zenn.dev/ubie_dev/feed"
        },
        {
            "name": "LayerX",
            "url": "https://tech.layerx.co.jp/feed"
        },
        {
            "name": "Money Forward",
            "url": "https://moneyforward-dev.jp/feed/"
        },
        {
            "name": "CARTA HOLDINGS",
            "url": "https://techblog.cartaholdings.co.jp/feed"
        },
        {
            "name": "ドリコム",
            "url": "https://tech.drecom.co.jp/feed/"
        },
        {
            "name": "Zlab",
            "url": "https://www.z-lab.co.jp/blog/feed/"
        },
        {
            "name": "BASE",
            "url": "https://devblog.thebase.in/rss.xml"
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
                # 外部キー制約のため、先に通知履歴を削除
                notified_count = db.query(NotifiedArticle).count()
                db.query(NotifiedArticle).delete()
                print(f"通知履歴 {notified_count} 件を削除しました。")

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
