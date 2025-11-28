# Heroku デプロイ手順書

## 📋 前提条件

- Heroku CLIがインストールされていること
- Herokuアカウントがあること
- Gitがインストールされていること

## 🚀 デプロイ手順

### 1. Heroku CLIのインストール（未インストールの場合）

```bash
# macOS
brew tap heroku/brew && brew install heroku

# または公式サイトからダウンロード
# https://devcenter.heroku.com/articles/heroku-cli
```

### 2. Herokuにログイン

```bash
heroku login
```

### 3. Herokuアプリを作成

```bash
# アプリ名は任意（グローバルでユニークな名前が必要）
heroku create your-slack-bot-name

# または自動生成
heroku create
```

### 4. Container Registryを有効化

```bash
heroku stack:set container -a your-slack-bot-name
```

### 5. Heroku Postgresアドオンを追加

```bash
# Miniプラン（月$5）
heroku addons:create heroku-postgresql:mini -a your-slack-bot-name

# または無料のHobby Devプラン（制限あり）
# heroku addons:create heroku-postgresql:hobby-dev -a your-slack-bot-name
```

### 6. 環境変数を設定

```bash
# Slack Webhook URL（必須）
heroku config:set SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL -a your-slack-bot-name

# 通知時刻（デフォルト: 09:00）
heroku config:set NOTIFICATION_TIME=09:00 -a your-slack-bot-name

# 記事の期間制限（デフォルト: 7日）
heroku config:set ARTICLE_AGE_LIMIT_DAYS=7 -a your-slack-bot-name

# 公開日時不明の記事を許可（デフォルト: true）
heroku config:set ALLOW_UNKNOWN_DATE=true -a your-slack-bot-name

# キーワードフィルタを有効化（デフォルト: true）
heroku config:set ENABLE_KEYWORD_FILTER=true -a your-slack-bot-name

# 除外キーワード
heroku config:set EXCLUDE_KEYWORDS="開催,お知らせ,募集,採用,Advent Calendar" -a your-slack-bot-name

# タイムゾーン
heroku config:set TZ=Asia/Tokyo -a your-slack-bot-name
```

### 7. Gitリポジトリにコミット

```bash
# まだGitリポジトリでない場合
git init
git add .
git commit -m "Initial commit for Heroku deployment"
```

### 8. Herokuにデプロイ

```bash
# Heroku remoteを追加
heroku git:remote -a your-slack-bot-name

# プッシュしてデプロイ
git push heroku main

# またはmasterブランチの場合
# git push heroku master
```

### 9. デプロイ状況を確認

```bash
# ログを確認
heroku logs --tail -a your-slack-bot-name

# アプリの状態を確認
heroku ps -a your-slack-bot-name
```

### 10. 初期データを投入

```bash
# Heroku上でスクリプトを実行
heroku run python scripts/init_data.py -a your-slack-bot-name
```

### 11. Heroku Schedulerを設定

```bash
# Heroku Schedulerアドオンを追加
heroku addons:create scheduler:standard -a your-slack-bot-name

# Schedulerダッシュボードを開く
heroku addons:open scheduler -a your-slack-bot-name
```

ダッシュボードで以下を設定：

- **Job Command**: `python src/scripts/run_notification.py`
- **Frequency**: `Every day at...`
- **Time**: `00:00 UTC`（日本時間9:00 = UTC 00:00）

> ⚠️ **重要**: Heroku Schedulerは**UTC時間**で動作します。
> 日本時間9:00に実行したい場合は、UTC 00:00に設定してください。

### 12. 動作確認

```bash
# 手動でテスト実行
heroku run python src/scripts/run_notification.py -a your-slack-bot-name

# APIエンドポイントにアクセス
curl https://your-slack-bot-name.herokuapp.com/health
```

## 🔧 トラブルシューティング

### ログの確認

```bash
# リアルタイムでログを確認
heroku logs --tail -a your-slack-bot-name

# 最新500行のログを確認
heroku logs -n 500 -a your-slack-bot-name
```

### データベース接続の確認

```bash
# データベース情報を確認
heroku pg:info -a your-slack-bot-name

# データベースに接続
heroku pg:psql -a your-slack-bot-name
```

### 環境変数の確認

```bash
# 全ての環境変数を表示
heroku config -a your-slack-bot-name

# 特定の環境変数を確認
heroku config:get SLACK_WEBHOOK_URL -a your-slack-bot-name
```

### デプロイのやり直し

```bash
# 最新の変更をコミット
git add .
git commit -m "Update configuration"

# 再デプロイ
git push heroku main
```

### アプリの再起動

```bash
heroku restart -a your-slack-bot-name
```

## 📊 コスト

| リソース | プラン | 月額 |
|---------|--------|------|
| Web Dyno | Basic | $7 |
| Heroku Postgres | Mini | $5 |
| Heroku Scheduler | Standard | 無料（Dynoの稼働時間に含まれる） |
| **合計** | | **$12/月** |

## 🔄 更新とメンテナンス

### コードの更新

```bash
# 変更をコミット
git add .
git commit -m "Update code"

# Herokuにプッシュ
git push heroku main
```

### 環境変数の更新

```bash
# 環境変数を更新
heroku config:set ARTICLE_AGE_LIMIT_DAYS=14 -a your-slack-bot-name

# 変更を反映するためにアプリを再起動
heroku restart -a your-slack-bot-name
```

### 通知履歴のリセット

```bash
heroku run python scripts/reset_notifications.py -a your-slack-bot-name
```

## 🔗 便利なコマンド

```bash
# アプリをブラウザで開く
heroku open -a your-slack-bot-name

# データベースのバックアップ
heroku pg:backups:capture -a your-slack-bot-name

# バックアップのダウンロード
heroku pg:backups:download -a your-slack-bot-name

# アプリの削除（注意！）
heroku apps:destroy your-slack-bot-name
```

## 📚 参考リンク

- [Heroku Container Registry](https://devcenter.heroku.com/articles/container-registry-and-runtime)
- [Heroku Postgres](https://devcenter.heroku.com/articles/heroku-postgresql)
- [Heroku Scheduler](https://devcenter.heroku.com/articles/scheduler)
- [Heroku Config Vars](https://devcenter.heroku.com/articles/config-vars)
