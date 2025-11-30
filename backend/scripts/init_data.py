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
            "name": "LINEヤフー",
            "url": "https://techblog.lycorp.co.jp/ja/feed/index.xml"
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
        # {
        #     "name": "ヤフー",
        #     "url": "https://techblog.yahoo.co.jp/feed/"
        # },
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

        # スタートアップ・メガベンチャー系（15件）
        {
            "name": "SmartHR",
            "url": "https://tech.smarthr.jp/feed"
        },
        {
            "name": "Timee",
            "url": "https://tech.timee.co.jp/feed"
        },
        {
            "name": "READYFOR",
            "url": "https://tech.readyfor.jp/feed"
        },
        {
            "name": "10X",
            "url": "https://product.10x.co.jp/feed"
        },
        {
            "name": "ビズリーチ",
            "url": "https://www.bizreach.co.jp/tech-blog/feed/"
        },
        {
            "name": "Visional",
            "url": "https://engineering.visional.inc/blog/feed"
        },
        {
            "name": "プレイド",
            "url": "https://tech.plaid.co.jp/feed"
        },
        {
            "name": "ココナラ",
            "url": "https://coconala-tech.com/feed/"
        },
        {
            "name": "MICIN",
            "url": "https://tech-blog.micin.jp/feed"
        },
        {
            "name": "スタディサプリ",
            "url": "https://blog.studysapuri.jp/feed"
        },
        {
            "name": "Ateam",
            "url": "https://www.a-tm.co.jp/top/blog/feed/"
        },
        {
            "name": "アンドパッド",
            "url": "https://tech.andpad.co.jp/feed"
        },
        {
            "name": "ラクスル",
            "url": "https://tech.raksul.com/feed"
        },
        {
            "name": "カケハシ",
            "url": "https://kakehashi-dev.hatenablog.com/rss"
        },
        {
            "name": "Wantedly",
            "url": "https://www.wantedly.com/companies/wantedly/feed"
        },

        # ゲーム会社系（8件）
        {
            "name": "Cygames",
            "url": "https://tech.cygames.co.jp/feed/"
        },
        {
            "name": "コロプラ",
            "url": "https://colopl.dev/feed"
        },
        {
            "name": "アカツキ",
            "url": "https://hackerslab.aktsk.jp/feed"
        },
        {
            "name": "QualiArts",
            "url": "https://technote.qualiarts.jp/feed"
        },
        {
            "name": "gumi",
            "url": "https://developers.gu3.co.jp/feed"
        },
        {
            "name": "KLab",
            "url": "https://www.klab.com/jp/blog/tech/feed/"
        },
        {
            "name": "セガ",
            "url": "https://techblog.sega.jp/feed"
        },
        {
            "name": "Craft Egg",
            "url": "https://tech.craftegg.jp/feed"
        },

        # 決済・金融系（7件）
        {
            "name": "PayPay",
            "url": "https://tech.paypay.ne.jp/rss.xml"
        },
        {
            "name": "GMOインターネット",
            "url": "https://recruit.gmo.jp/engineer/jisedai/blog/feed/"
        },
        {
            "name": "GMOメディア",
            "url": "https://techblog.gmo-media.jp/feed"
        },
        {
            "name": "Kyash",
            "url": "https://blog.kyash.co/feed"
        },
        {
            "name": "bitFlyer",
            "url": "https://blog.bitflyer.com/feed"
        },
        {
            "name": "Coincheck",
            "url": "https://tech.coincheck.blog/feed"
        },
        {
            "name": "Moneytree",
            "url": "https://getmoneytree.com/jp/blog/feed/"
        },

        # メディア・広告系（5件）
        {
            "name": "エムスリー",
            "url": "https://www.m3tech.blog/feed"
        },
        {
            "name": "オプト",
            "url": "https://tech-blog.opt.ne.jp/feed"
        },
        {
            "name": "サイボウズ",
            "url": "https://blog.cybozu.io/feed"
        },
        {
            "name": "pixiv",
            "url": "https://inside.pixiv.blog/feed"
        },
        {
            "name": "note",
            "url": "https://note.com/notemag/m/m5b7aea49c9b1/rss"
        },

        # 大手IT・SIer系（5件）
        {
            "name": "NTTコミュニケーションズ",
            "url": "https://engineers.ntt.com/feed"
        },
        {
            "name": "NTTデータ",
            "url": "https://www.nttdata.com/jp/ja/news/blog/feed/"
        },
        {
            "name": "リクルートテクノロジーズ",
            "url": "https://recruit-tech.co.jp/blog/feed/"
        },
        {
            "name": "富士通",
            "url": "https://www.fujitsu.com/jp/products/software/developer-tool/blog/feed/"
        },
        {
            "name": "日立製作所",
            "url": "https://www.hitachi.co.jp/rd/portal/feed/"
        },

        # EC・マーケットプレイス系（5件）
        {
            "name": "ヤプリ",
            "url": "https://tech.yappli.io/feed"
        },
        {
            "name": "オイシックス・ラ・大地",
            "url": "https://creators.oisix.com/feed"
        },
        {
            "name": "PKSHA Technology",
            "url": "https://www.pkshatech.com/ja/blog/feed/"
        },
        {
            "name": "ラクマ",
            "url": "https://tech.rakus.co.jp/feed/"
        },
        {
            "name": "Zホールディングス",
            "url": "https://www.z-holdings.co.jp/ja/blog/feed/"
        },

        # その他有力企業（5件）
        {
            "name": "弁護士ドットコム",
            "url": "https://creators.bengo4.com/feed"
        },
        {
            "name": "Uzabase",
            "url": "https://tech.uzabase.com/feed"
        },
        {
            "name": "トレタ",
            "url": "https://tech.toreta.in/feed"
        },
        {
            "name": "フィードフォース",
            "url": "https://developer.feedforce.jp/feed"
        },
        {
            "name": "ペライチ",
            "url": "https://peraichi.hatenablog.jp/rss"
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
