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

## 📝 初期データの投入

Docker環境が起動したら、初期データ（RSS情報源）を投入します。

```bash
docker-compose exec app python scripts/init_data.py
```

このスクリプトで、以下の日本企業の技術ブログRSSが登録されます：

- メルカリ
- サイバーエージェント
- LINE
- 楽天
- DeNA
- クックパッド
- ヤフー
- リクルート
- はてな
- ミクシィ
- GMOペパボ
- ZOZO

## 🧪 テスト

### 手動でSlack通知をテストする

```bash
curl -X POST http://localhost:8000/trigger-notification
```

### 登録されているRSS情報源を確認

```bash
curl http://localhost:8000/sources
```

## 📊 API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/` | ヘルスチェック |
| GET | `/health` | 詳細なヘルスチェック |
| GET | `/sources` | 登録されているRSS情報源の一覧 |
| POST | `/trigger-notification` | 手動で通知を実行（テスト用） |

## ⏰ スケジュール設定

デフォルトでは、**毎日9:00（JST）**に自動的に通知が実行されます。

通知時刻を変更したい場合は、`.env` ファイルの `NOTIFICATION_TIME` を編集してください：

```env
NOTIFICATION_TIME=09:00  # HH:MM形式
```

## 🔍 トラブルシューティング

### データベース接続エラー

```bash
# データベースコンテナの状態を確認
docker-compose ps

# データベースログを確認
docker-compose logs db
```

### Slack通知が送信されない

1. `.env` ファイルの `SLACK_WEBHOOK_URL` が正しいか確認
2. 手動テストを実行してログを確認

```bash
curl -X POST http://localhost:8000/trigger-notification
docker-compose logs app
```

### RSS取得に失敗する

一部のRSSフィードが取得できない場合があります。ログを確認してください：

```bash
docker-compose logs -f app | grep ERROR
```

## 📄 ライセンス

MIT License
