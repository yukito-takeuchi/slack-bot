"""通知履歴をリセットするスクリプト"""
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.database import SessionLocal
from src.models import NotifiedArticle


def reset_notifications():
    """通知履歴を全削除"""
    db = SessionLocal()

    try:
        # 削除前の件数を取得
        count_before = db.query(NotifiedArticle).count()

        print(f"現在の通知履歴件数: {count_before}件")

        if count_before == 0:
            print("通知履歴は既に空です。")
            return

        # 確認
        response = input(f"\n{count_before}件の通知履歴を削除しますか？ (y/N): ")

        if response.lower() == 'y':
            # 全削除
            db.query(NotifiedArticle).delete()
            db.commit()

            # 削除後の件数を確認
            count_after = db.query(NotifiedArticle).count()

            print(f"\n✅ 通知履歴を削除しました。")
            print(f"削除前: {count_before}件")
            print(f"削除後: {count_after}件")
            print("\n次回のAPI実行時に、全記事が再度通知対象になります。")
        else:
            print("キャンセルしました。")

    except Exception as e:
        db.rollback()
        print(f"❌ エラーが発生しました: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("通知履歴リセットスクリプト")
    print("=" * 60)
    print()

    reset_notifications()

    print()
    print("=" * 60)
    print("完了しました！")
    print("=" * 60)
