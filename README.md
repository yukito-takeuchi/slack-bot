# Slack通知Bot

日本企業を中心とした高品質な技術ブログの最新記事を自動収集し、Slackに定時通知するBot

## 📋 機能

- RSS フィードから最新の技術記事を自動収集
- 二重通知防止（既読記事の管理）
- 毎日定時（9:00 JST）にSlackへ自動通知
- Docker Compose による簡単なローカル環境構築

## 🛠 技術スタック

- **バックエンド**: Python 3.11 + FastAPI
- **データベース**: PostgreSQL 15
- **インフラ**: Docker + Docker Compose
- **スケジューラー**: APScheduler
- **RSS パーサー**: feedparser

## 📁 プロジェクト構造

```
slack-bot/
├── backend/
│   ├── src/
│   │   ├── api/          # API エンドポイント
│   │   ├── config/       # 設定ファイル
│   │   ├── models/       # データベースモデル
│   │   ├── scheduler/    # スケジューラー
│   │   ├── services/     # ビジネスロジック
│   │   └── main.py       # アプリケーションエントリーポイント
│   ├── tests/            # テストコード
│   ├── migrations/       # データベースマイグレーション
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd slack-bot
```

### 2. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、必要な値を設定します。

```bash
cp .env.example .env
```

`.env` ファイルを編集：

```env
# Slack Webhook URL（必須）
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# その他の設定はデフォルト値でOK
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=slack_bot
NOTIFICATION_TIME=09:00
```

### 3. Docker Compose で起動

```bash
docker-compose up -d
```

初回起動時は、イメージのビルドに数分かかります。

### 4. 動作確認

APIが正常に起動しているか確認：

```bash
curl http://localhost:8000/health
```

以下のようなレスポンスが返れば成功です：

```json
{
  "status": "healthy",
  "service": "slack-bot",
  "version": "1.0.0"
}
```

## 📊 データベース

PostgreSQLコンテナが自動的に起動し、以下のテーブルが作成されます：

- `rss_sources`: RSS情報源の管理
- `notified_articles`: 通知済み記事の管理

## 🔧 開発

### ログの確認

```bash
# すべてのログを表示
docker-compose logs -f

# アプリケーションのログのみ
docker-compose logs -f app

# データベースのログのみ
docker-compose logs -f db
```

### コンテナの停止

```bash
docker-compose down
```

### コンテナとボリュームの完全削除

```bash
docker-compose down -v
```

### データベースに接続

```bash
docker-compose exec db psql -U postgres -d slack_bot
```

## 📝 次のステップ

1. データベースモデルの実装
2. RSS収集機能の実装
3. Slack通知機能の実装
4. スケジューラーの設定
5. 初期データ（RSS情報源）の投入

## 📄 ライセンス

MIT License
