"""取得した記事を表示して分析するスクリプト"""
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.database import SessionLocal
from src.services import RSSService


def show_articles():
    """全RSS情報源から記事を取得して表示"""
    db = SessionLocal()

    try:
        service = RSSService(db)
        new_articles = service.get_new_articles()

        if not new_articles:
            print("取得された記事はありません。")
            return

        print(f"\n取得された記事: {len(new_articles)}件\n")
        print("=" * 100)

        for i, article in enumerate(new_articles, 1):
            title = article.get("title", "No Title")
            url = article.get("article_url", "")
            source_name = article.get("source_name", "Unknown")
            published_at = article.get("published_at")

            date_str = published_at.strftime("%Y-%m-%d") if published_at else "日付不明"

            print(f"{i}. [{source_name}] {title}")
            print(f"   日付: {date_str}")
            print(f"   URL: {url}")
            print("-" * 100)

        # キーワード分析
        print("\n" + "=" * 100)
        print("タイトルに含まれるキーワード分析")
        print("=" * 100)

        # よくある非技術記事のキーワード候補
        potential_keywords = [
            "イベント", "登壇", "開催", "参加", "募集", "採用",
            "インタビュー", "紹介", "お知らせ", "リリース",
            "セミナー", "勉強会", "ミートアップ", "Meetup",
            "新卒", "中途", "エンジニア募集", "求人",
            "LT", "発表", "スライド"
        ]

        keyword_counts = {}
        for keyword in potential_keywords:
            count = sum(1 for article in new_articles if keyword in article.get("title", ""))
            if count > 0:
                keyword_counts[keyword] = count

        if keyword_counts:
            print("\n検出されたキーワード:")
            for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  - '{keyword}': {count}件")
        else:
            print("\n候補キーワードは検出されませんでした。")

    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 100)
    print("記事一覧表示スクリプト")
    print("=" * 100)

    show_articles()

    print("\n" + "=" * 100)
    print("完了しました！")
    print("=" * 100)
