# 筋トレマッチングアプリ

## 概要
筋トレでの合トレ仲間を見つけるためのマッチング＆チャットアプリです。

## 主な機能
- プロフィール登録・編集
- ユーザー検索、いいね、マッチング
- チャット機能
- 通知・おすすめユーザー表示

## 使用技術・ライブラリ
| 種別 | 内容 |
|------|------|
| フレームワーク | Django 5.2.4 |
| バックエンド | Python |
| フロントエンド | HTML（Djangoテンプレート） / JS（Vanilla） |
| データベース | 開発：MySQL / 本番：PostgreSQL（Render） |
| デプロイ | [Render](https://render.com)（無料枠） |
| 画像ストレージ | [Cloudinary](https://cloudinary.com/)（無料枠） |
| 認証 | Django標準の認証機能＋CustomUser |
| 静的ファイル収集 | WhiteNoise |
| その他 | gunicorn / python-decouple / dj-database-url など |

## デモ環境
- https://withtraining-app.onrender.com

※無料枠で構築しているため、アクセスに時間がかかる場合があります。

## セットアップ手順（ローカル開発環境用）
```bash
# 1. リポジトリをクローン
git clone https://github.com/nico25-18/withTraining-app.git
cd withTraining-app

# 2. 仮想環境を作成・有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. パッケージをインストール
pip install -r requirements.txt

# 4. .envファイルを作成して環境変数を設定
cp .env.example .env  # 内容は.env.exampleを編集

# 5. DBマイグレーションと起動
python manage.py migrate
python manage.py runserver
