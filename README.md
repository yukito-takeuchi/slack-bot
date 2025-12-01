# Tech Blog Notification Bot

> 日本企業 80 社の技術ブログ RSS を監視し、新着記事を Slack に自動通知する Bot

---

## 📖 概要

日本の有力 IT 企業 80 社の技術ブログを毎日監視し、新着記事を Slack に自動通知するシステムです。スレッド機能と URL unfurl 機能を活用し、見やすく情報整理された通知を実現しています。

---

## 🏗️ システム構成

```mermaid
graph TB
    subgraph "Frontend"
        UI1[Slack<br/>通知受信]
        UI2[Next.js<br/>設定画面]
    end

    subgraph "Scheduler"
        A[APScheduler<br/>毎日09:00 JST]
    end

    subgraph "Backend"
        B[FastAPI<br/>REST API]
        C[RSS Service<br/>フィード取得]
        D[Slack Service<br/>通知送信]
        E[Notification Service<br/>オーケストレーション]
    end

    subgraph "Database"
        F[PostgreSQL<br/>rss_sources<br/>notified_articles]
    end

    subgraph "External Services"
        G[Slack API<br/>chat.postMessage<br/>Thread & Unfurl]
        H[RSS Feeds<br/>80社の技術ブログ]
    end

    subgraph "Infrastructure"
        I[Docker Compose<br/>ローカル開発環境]
        J[Heroku<br/>本番環境]
    end

    A -->|トリガー| E
    E -->|記事取得| C
    C -->|RSS取得| H
    C -->|保存/確認| F
    E -->|通知| D
    D -->|投稿| G
    G -->|表示| UI1
    UI2 -->|API Call| B
    B -->|実行| A
    I -->|Container| B
    I -->|Container| F
    B -->|Deploy| J

    style UI1 fill:#e01e5a
    style UI2 fill:#61dafb
    style A fill:#ff6b6b
    style B fill:#009688
    style C fill:#4caf50
    style D fill:#2196f3
    style E fill:#9c27b0
    style F fill:#336791
    style G fill:#e01e5a
    style H fill:#ff9800
    style I fill:#2496ed
    style J fill:#430098
```

---

## 🛠️ 使用技術

### Backend

| 技術        | 用途                       |
| ----------- | -------------------------- |
| Python 3.11 | プログラミング言語         |
| FastAPI     | REST API フレームワーク    |
| SQLAlchemy  | ORM（データベース操作）    |
| feedparser  | RSS フィード解析           |
| APScheduler | スケジューラー（定期実行） |
| requests    | HTTP 通信                  |

### Database

| 技術       | 用途               |
| ---------- | ------------------ |
| PostgreSQL | メインデータベース |

### External Services

| 技術             | 用途               |
| ---------------- | ------------------ |
| Slack Bot API    | チャンネル通知     |
| chat.postMessage | メッセージ投稿     |
| Thread 機能      | スレッド返信       |
| Unfurl 機能      | URL プレビュー表示 |

### Infrastructure

| 技術                      | 用途                 |
| ------------------------- | -------------------- |
| Docker                    | コンテナ化           |
| Docker Compose            | ローカル開発環境     |
| Heroku                    | 本番環境ホスティング |
| Heroku Container Registry | Docker デプロイ      |
| Heroku Scheduler          | 定期実行             |

---

## 🗄️ データベース設計（ER 図）

```mermaid
erDiagram
    rss_sources ||--o{ notified_articles : has

    rss_sources {
        serial id PK
        varchar name "企業名"
        varchar url "RSS Feed URL"
        boolean is_active "有効/無効"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    notified_articles {
        serial id PK
        varchar article_url "記事URL UNIQUE"
        varchar title "記事タイトル"
        timestamp published_at "公開日時"
        integer source_id FK "RSS情報源ID"
        timestamp notified_at "通知日時"
    }
```

---

## ✨ 主な機能

### 📰 RSS 巡回機能

- ✅ **80 社の技術ブログ監視**
  - メルカリ、サイバーエージェント、LINE、楽天、DeNA など
  - スタートアップから大手企業まで網羅
- 🕐 **定期実行**: 毎日 09:00（JST）に自動実行
- 📅 **期間フィルタ**: 過去 30 日以内の記事のみ取得
- 🚫 **キーワード除外**: イベント・採用情報を自動除外
  - 除外キーワード: 開催、お知らせ、募集、採用、Advent Calendar、出展、参加、イベント
- 🔄 **重複防止**: 通知済み記事を DB で管理

### 💬 Slack 通知機能

- 📱 **スレッド形式で通知**
  - メイン投稿: 記事数と統計情報のサマリー
  - スレッド内: 各記事の詳細（個別メッセージ）
- 🖼️ **URL unfurl 機能**
  - OGP 画像・タイトル・説明文を自動表示
  - 1 時間制限を回避（ハッシュフラグメント使用）
- 🔢 **記事 ID 表示**: #1, #2, #3... で参照しやすく
- 📊 **統計情報表示**
  - 監視中サイト数
  - 取得成功サイト数
  - エラー情報
- ⚠️ **エラーハンドリング**
  - RSS 取得失敗時のエラー詳細表示
  - 記事 0 件でも通知を送信

---

## 💡 工夫した点・技術的チャレンジ

### 1. Slack スレッド機能の活用

**課題:**

- 1 日 10-20 件の記事通知でチャンネルが埋まる
- 過去の通知を遡るのが困難

**解決策:**

- メイン投稿: 簡潔なサマリー（3-4 行）
- スレッド内: 詳細な記事一覧
- チャンネルがスッキリ、詳細はスレッドで確認

**実装:**

```python
# メイン投稿
thread_ts = self.post_message(main_message)

# スレッド返信
for article in articles:
    self.post_message(article_message, thread_ts=thread_ts)
```

---

### 2. URL unfurl 1 時間制限の回避

**課題:**

- Slack は同じ URL を 1 時間以内に再投稿すると、unfurl（プレビュー表示）をスキップ
- テスト時や同じ記事の再投稿で問題

**解決策:**

- URL にユニークなハッシュフラグメントを追加
- `https://example.com/article#a1b2c3d4`
- ブラウザは `#` 以降を無視するため、同じページに飛ぶ
- Slack は「異なる URL」と認識して unfurl を実行

**実装:**

```python
import hashlib
import time

unique_hash = hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()[:8]
url_with_hash = f"{url}#{unique_hash}"
```

---

### 3. 各記事を個別メッセージで投稿

**課題:**

- 1 つのメッセージに複数 URL があると、unfurl が発火しない

**解決策:**

- ヘッダーメッセージ: `📄 新着記事一覧`
- 各記事を個別メッセージとして投稿
- 全ての URL で unfurl が確実に発火

**Before:**

```python
# 全記事を1メッセージにまとめる（unfurl発火しない）
message = "記事1\nURL1\n\n記事2\nURL2..."
post_message(message)
```

**After:**

```python
# 各記事を個別に投稿（unfurl発火する）
for article in articles:
    post_message(format_article(article))
```

---

### 4. 重複通知防止

**課題:**

- 同じ記事を複数回通知してしまう

**解決策:**

- `notified_articles` テーブルで通知履歴を管理
- 記事 URL（UNIQUE 制約）で重複チェック
- 未通知の記事のみを通知対象とする

**実装:**

```python
def is_article_notified(self, article_url: str) -> bool:
    existing = self.db.query(NotifiedArticle).filter(
        NotifiedArticle.article_url == article_url
    ).first()
    return existing is not None
```

---

### 5. HTML エンティティデコード対応

**課題:**

- RSS 内のタイトルに `&#038;` などの HTML エンティティが含まれる
- キーワードフィルタが正しく動作しない

**解決策:**

- `html.unescape()` でデコード
- `&#038;` → `&` に変換してからキーワードマッチング

**実装:**

```python
import html

decoded_title = html.unescape(title)  # &#038; → &
if keyword.lower() in decoded_title.lower():
    return True
```

---

### 6. 記事 0 件でも必ず通知

**課題:**

- 記事 0 件の日は通知なし → 機能が動いているか不明

**解決策:**

- 記事 0 件でも統計情報を通知
- 「本日の新着記事はありません」メッセージ
- 監視中サイト数、取得成功数を表示

**Before:**

```python
if not articles:
    return  # 何も通知しない
```

**After:**

```python
# 記事0件でも必ず通知
send_notification(
    articles=[],  # 空でもOK
    total_sources=80,
    successful_sources=78
)
```

---

### 7. エラー情報の可視化

**課題:**

- RSS 取得失敗がログにしか残らない
- ユーザーに問題が見えない

**解決策:**

- エラー情報をスレッドに投稿
- サイト名とエラー内容を表示
- 最大 10 件までリスト表示

**スレッド内:**

```
⚠️ 取得エラー詳細

- PayPay (タイムアウト)
- Cygames (フィード取得失敗)
- note (記事なし)
```

---

## 📂 プロジェクト構造

```
slack-bot/
├── frontend/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   │   ├── database.py         # DB接続設定
│   │   │   └── settings.py         # 環境変数管理
│   │   ├── models/
│   │   │   └── __init__.py         # RSSSource, NotifiedArticle
│   │   ├── services/
│   │   │   ├── rss_service.py      # RSS取得・解析
│   │   │   ├── slack_service.py    # Slack通知
│   │   │   └── notification_service.py  # オーケストレーション
│   │   └── main.py                 # FastAPI アプリケーション
│   ├── scripts/
│   │   ├── init_data.py            # 初期データ投入（80社）
│   │   └── reset_notifications.py  # 通知履歴リセット
│   ├── .env.example                # 環境変数テンプレート
│   ├── requirements.txt            # Python依存関係
│   └── Dockerfile                  # Dockerイメージ定義
│
├── docker-compose.yml              # ローカル開発環境
├── Dockerfile                      # Heroku用Dockerfile
├── heroku.yml                      # Heroku設定
├── SLACK_APP_SETUP.md              # Slack App設定手順
└── README.md
```

---

## 🚀 セットアップ

### 1. 環境変数設定

`backend/.env` ファイルを作成：

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/slack_bot

# Slack Bot Token（スレッド機能に必要）
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL_ID=C01234567AB

# Notification
NOTIFICATION_TIME=09:00

# Article Filtering
ARTICLE_AGE_LIMIT_DAYS=30
ALLOW_UNKNOWN_DATE=true

# Keyword Filtering
ENABLE_KEYWORD_FILTER=true
EXCLUDE_KEYWORDS=開催,お知らせ,募集,採用,Advent Calendar,出展,参加,イベント

# Timezone
TZ=Asia/Tokyo
```

### 2. Slack App 作成

詳細は `SLACK_APP_SETUP.md` を参照

**必要な権限:**

- `chat:write`
- `chat:write.public`

**取得する情報:**

- Bot Token: `xoxb-...`
- Channel ID: `C...`

### 3. ローカル環境起動

```bash
# Dockerコンテナ起動
docker-compose up -d

# 初期データ投入（80社のRSS情報源）
docker exec -it slack-bot-backend bash
python scripts/init_data.py

# 通知テスト実行
python -c "from src.config.database import SessionLocal; from src.services.notification_service import NotificationService; db = SessionLocal(); service = NotificationService(db); service.run(); db.close()"
```

### 4. Heroku デプロイ

```bash
# Heroku CLI ログイン
heroku login

# Heroku アプリ作成
heroku create your-slack-bot-name

# PostgreSQL addon追加
heroku addons:create heroku-postgresql:essential-0

# 環境変数設定
heroku config:set SLACK_BOT_TOKEN="xoxb-..." -a your-slack-bot-name
heroku config:set SLACK_CHANNEL_ID="C..." -a your-slack-bot-name
heroku config:set NOTIFICATION_TIME="09:00" -a your-slack-bot-name

# Heroku Container Registryにログイン
heroku container:login

# デプロイ
git push heroku main

# Heroku Scheduler設定
heroku addons:create scheduler:standard -a your-slack-bot-name
heroku addons:open scheduler -a your-slack-bot-name

# スケジューラーで以下を設定：
# コマンド: python run_notification.py
# 頻度: Every day at 09:00 AM (JST)
```

---

## 📊 監視対象企業（80 社）

### スタートアップ・メガベンチャー系（45 社）

メルカリ、サイバーエージェント、LINE、楽天、DeNA、クックパッド、ヤフー、リクルート、はてな、ミクシィ、GMO ペパボ、ZOZO、Sansan、SmartNews、Retty、ドワンゴ、カオナビ、Chatwork、eureka、freee、GREE、Gunosy、Indeed、Ubie、LayerX、Money Forward、CARTA HOLDINGS、ドリコム、Zlab、BASE、SmartHR、Timee、READYFOR、10X、ビズリーチ、Visional、プレイド、ココナラ、MICIN、スタディサプリ、Ateam、アンドパッド、ラクスル、カケハシ、Wantedly

### ゲーム会社系（8 社）

Cygames、コロプラ、アカツキ、QualiArts、gumi、KLab、セガ、Craft Egg

### 決済・金融系（7 社）

PayPay、GMO インターネット、GMO メディア、Kyash、bitFlyer、Coincheck、Moneytree

### メディア・広告系（5 社）

エムスリー、オプト、サイボウズ、pixiv、note

### 大手 IT・SIer 系（5 社）

NTT コミュニケーションズ、NTT データ、リクルートテクノロジーズ、富士通、日立製作所

### EC・マーケットプレイス系（5 社）

ヤプリ、オイシックス・ラ・大地、PKSHA Technology、ラクマ、Z ホールディングス

### その他有力企業（5 社）

弁護士ドットコム、Uzabase、トレタ、フィードフォース、ペライチ

---

## 📸 Slack 通知例

### メイン投稿（チャンネル）

```
📰 【本日の技術ブログ更新】2025-01-15 09:00

✅ 新着記事: 12件

📊 監視中: 80サイト | 取得成功: 78サイト

💬 詳細はスレッドで確認 →
```

### スレッド内（記事一覧）

```
📄 新着記事一覧
```

```
#1 [SmartHR] QAエンジニアがSmartHRに転職して4ヶ月で感じたこと
公開日: 2025-11-28
https://tech.smarthr.jp/entry/2025/11/28/170000#a1b2c3d4
[OGP画像プレビュー表示]
```

```
#2 [メルカリ] GraphQLのパフォーマンス改善による応答速度の向上
公開日: 2025-01-14
https://engineering.mercari.com/blog/entry/2025-01-14#e5f6g7h8
[OGP画像プレビュー表示]
```

### スレッド内（エラー情報）

```
⚠️ 取得エラー詳細

- PayPay (タイムアウト)
- Cygames (フィード取得失敗)
```

---

## 🎯 今後の改善予定

- [ ] Web ダッシュボード（記事一覧・検索機能）
- [ ] 企業ごとの通知 ON/OFF 設定
- [ ] キーワードアラート機能
- [ ] 週次サマリーレポート
- [ ] 記事の人気度スコアリング
- [ ] カテゴリ別フィルタリング

---

## 📄 License

MIT License
