# EVOL - Evolving Visual Observability Layer

[![CI](https://github.com/capybara-works/EVOL/actions/workflows/ci.yml/badge.svg)](https://github.com/capybara-works/EVOL/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**ソフトウェアとファームウェアの進化における不変の事実の記憶**


## 概要

EVOL v1は、CI/CD実行とハードウェアテストを統一タイムラインで記録する観察基盤です。「何が起きたか」のみを記録し、解釈や最適化は行いません。

### 主要特徴

- 🔍 **非侵襲的CI観察**: GitHub Actionsの実行履歴、メタデータ、アーティファクトを自動収集
- 🔌 **ハードウェアテレメトリ**: デバイスセッションダンプと信号データの保存
- 🛠️ **バイナリ逆アセンブリ**: `objdump`を使用したELFファイルの自動逆アセンブリ
- 📊 **統一データモデル**: すべてのデータが`Run`に紐づく明確な設計
- 📈 **可視化**: Grafanaダッシュボードによる統合タイムラインとメトリクス表示

### 設計原則

- **Observer Only (観察者)**: データの観察と記録のみ、意味解析は外部システムへ
- **Immutable (不変)**: 一度記録された履歴は変更されない
- **Unified (統一)**: CI実行とハードウェアテストを単一の概念で管理

## クイックスタート

### 前提条件

- Python 3.10以上
- Docker（Grafana用）
- `objdump`（逆アセンブリ用、オプション）

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/capybara-works/EVOL.git
cd EVOL

# 依存関係をインストール
pip install -e .

# または Poetry を使用
poetry install
```

### 環境設定

```bash
# 環境変数ファイルを作成
cp .env.example .env

# .env を編集してGitHub Personal Access Tokenを設定
# GITHUB_TOKEN=your_github_pat_here
```

### データベース初期化

```bash
# Alembicでデータベーススキーマを作成
alembic upgrade head
```

## ⚡ クイックスタート（推奨）

自動化スクリプトで簡単にセットアップ:

```bash
# 1. 自動セットアップ
./quickstart.sh

# 2-A. WebUI（最も簡単）
./start-ui.sh
# ブラウザで http://localhost:8080 にアクセス

# 2-B. CLIで同期＋Grafana起動
./sync_and_view.sh owner/repo
```

詳細な手順は以下を参照してください。

## 基本的な使い方

### 1. データ収集

**GitHubリポジトリのCI履歴を取得:**
```bash
export GITHUB_TOKEN=your_token
python -m evol.collector.sync --project owner/repo --include-disasm
```

**オプション:**
- `--since TIMESTAMP`: 指定日時以降のデータのみ取得
- `--include-disasm`: ELFアーティファクトの逆アセンブリを有効化
- `--retain-binaries`: ダウンロードしたバイナリファイルを保持

**ハードウェアテレメトリのインポート:**
```bash
python -m evol.collector.sync --import-device path/to/device_dump.bin
```

### 2. データの確認（API）

```bash
# APIサーバーを起動
uvicorn evol.api.main:app --reload

# ブラウザで http://localhost:8000/docs を開く
# または curlでアクセス
curl http://localhost:8000/api/v1/projects
```

### 3. 可視化（Grafana）

```bash
# Grafanaを起動
docker-compose up -d

# ブラウザで http://localhost:3000 を開く
# デフォルト認証: admin/admin
```

## ディレクトリ構造

```
evol/
├── evol/
│   ├── db/              # データベースモデルと接続
│   ├── collector/       # データ収集ロジック
│   └── api/             # FastAPI アプリケーション
├── alembic/             # データベースマイグレーション
├── dashboards/          # Grafana ダッシュボード定義
├── grafana/             # Grafana プロビジョニング設定
├── ARCHITECTURE.md      # 詳細な技術文書
├── README.md            # このファイル
└── docker-compose.yml   # Grafana コンテナ定義
```

## ドキュメント

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 完全なシステムアーキテクチャドキュメント
  - コンポーネント詳細
  - データベーススキーマ
  - APIリファレンス
  - 運用ガイドライン

- **[validation_report.md](.gemini/antigravity/brain/667022f8-0e6e-4484-a065-8b963cb4d0dd/validation_report.md)** - 実装妥当性検証レポート

## ユースケース

### ファームウェア開発チーム
- CI/CD実行履歴とハードウェアテスト結果を統合管理
- バイナリの変更履歴をアセンブリレベルで追跡

### QAエンジニア
- 過去のビルド成果物と実行結果を検索・比較
- 特定のコミットに対するテスト実行履歴を可視化

### DevOpsエンジニア
- パイプライン実行時間やアーティファクトサイズの推移をモニタリング
- 長期的なコードベース成長トレンドを分析

## トラブルシューティング

### `objdump not found`
逆アセンブリ機能を使用する場合は、`objdump`または`arm-none-eabi-objdump`がPATHに含まれている必要があります。

```bash
# macOS (Homebrew)
brew install binutils

# Ubuntu/Debian
sudo apt-get install binutils
```

### `GITHUB_TOKEN not found`
環境変数が設定されていることを確認してください:
```bash
echo $GITHUB_TOKEN
```

### Grafanaにデータが表示されない
1. `evol.db`ファイルが存在することを確認
2. データ収集が成功していることを確認（`python -m evol.collector.sync`の出力をチェック）
3. Grafanaのデータソース設定を確認

## 貢献

このプロジェクトへの貢献を歓迎します。Issue報告やPull Requestをお寄せください。

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

## 関連プロジェクト（計画中）

- **LPAD** (Log Pattern Anomaly Detection): EVOLデータの解析層
- **SEDA** (Software Evolution Decision Advisor): 最適化推奨システム

---

**Note**: EVOL v1は観察基盤です。データの解釈や最適化は意図的に含まれていません。
