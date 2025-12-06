# GitHub公開・開発ガイド

このドキュメントでは、EVOLプロジェクトのGitHub公開手順と、開発者向けのワークフローについて説明します。

---

## 📤 GitHub公開手順

### 前提条件

- Gitがインストールされていること
- GitHubアカウントを持っていること（`capybara-works` Organizationへのアクセス権）
- ローカルで開発が完了していること

### ステップ1: ローカルリポジトリの確認

```bash
cd /path/to/EVOL

# Gitステータスを確認
git status

# コミット済みであることを確認
git log --oneline -1
```

### ステップ2: GitHubでリポジトリを作成

#### 方法A: GitHub Web UI（推奨）

1. https://github.com/organizations/capybara-works/repositories/new にアクセス
2. 以下の設定で作成:
   - **Repository name**: `EVOL`
   - **Description**: `Evolving Visual Observability Layer - Immutable factual memory of software evolution`
   - **Visibility**: **Public**
   - ⚠️ **"Initialize this repository with a README" のチェックを外す**
   - ⚠️ **".gitignore" や "license" も選択しない**（既にローカルに存在するため）
3. 「Create repository」をクリック

#### 方法B: GitHub CLI

```bash
# GitHub CLIがインストールされている場合
gh auth login  # 初回のみ

gh repo create capybara-works/EVOL \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description "Evolving Visual Observability Layer - Immutable factual memory of software evolution"
```

### ステップ3: リモートリポジトリを追加してプッシュ

GitHub Web UIで作成した場合、以下を実行:

```bash
cd /Users/mitokouki/EVOL

# リモートリポジトリを追加
git remote add origin https://github.com/capybara-works/EVOL.git

# ブランチ名をmainに変更（必要に応じて）
git branch -M main

# プッシュ
git push -u origin main
```

### ステップ4: リポジトリの設定（オプション）

GitHubリポジトリページで以下を設定:

1. **Topics/Tags** を追加:
   - `observability`
   - `telemetry`
   - `firmware`
   - `ci-cd`
   - `hardware-testing`
   - `python`
   - `fastapi`
   - `grafana`

2. **About** セクションを編集:
   - Description: `Evolving Visual Observability Layer - Immutable factual memory of software evolution`
   - Website: （ドキュメントサイトがあれば）

3. **Settings** で以下を確認:
   - Issues: 有効
   - Projects: 有効（オプション）
   - Wiki: 無効（ARCHITECTUREmdで十分）

---

## 🏷️ リリースの作成

### バージョンタグの作成

```bash
# v1.0.0 タグを作成
git tag -a v1.0.0 -m "EVOL v1.0.0 - Initial Release"

# タグをプッシュ
git push origin v1.0.0
```

### GitHub Releaseの作成

1. https://github.com/capybara-works/EVOL/releases/new にアクセス
2. 以下を入力:
   - **Tag**: `v1.0.0`（既に作成済みのタグを選択）
   - **Release title**: `EVOL v1.0.0 - Initial Release`
   - **Description**:
     ```markdown
     # EVOL v1.0.0 - Initial Release
     
     ソフトウェアとファームウェアの進化における不変の事実の記憶を提供する観察基盤の初回リリースです。
     
     ## 主要機能
     
     - ✅ GitHub Actions CI/CD実行履歴の自動収集
     - ✅ ハードウェアテレメトリのインポート
     - ✅ ELFバイナリの逆アセンブリ保存
     - ✅ FastAPI による読み取り専用API
     - ✅ Grafana ダッシュボードによる可視化
     
     ## ドキュメント
     
     - [README.md](https://github.com/capybara-works/EVOL/blob/main/README.md)
     - [ARCHITECTURE.md](https://github.com/capybara-works/EVOL/blob/main/ARCHITECTURE.md)
     
     ## インストール
     
     ```bash
     git clone https://github.com/capybara-works/EVOL.git
     cd EVOL
     pip install -e .
     ```
     
     詳細はREADME.mdをご覧ください。
     ```
3. 「Publish release」をクリック

---

## 🔄 開発ワークフロー

### 新機能の開発

```bash
# 最新のmainブランチを取得
git checkout main
git pull origin main

# 機能ブランチを作成
git checkout -b feature/new-collector

# 開発
# ... コード編集 ...

# コミット
git add .
git commit -m "feat: Add new collector for X"

# プッシュ
git push origin feature/new-collector
```

### Pull Requestの作成

1. GitHubでPull Requestを作成
2. 変更内容を説明
3. レビューを依頼
4. Approve後にmainへマージ

### コミットメッセージの規約

Conventional Commitsに従う:

- `feat:` - 新機能
- `fix:` - バグ修正
- `docs:` - ドキュメントのみの変更
- `style:` - コードの意味に影響しない変更（空白、フォーマットなど）
- `refactor:` - バグ修正でも機能追加でもないコード変更
- `test:` - テストの追加や修正
- `chore:` - ビルドプロセスやツールの変更

例:
```bash
git commit -m "feat: Add PostgreSQL support to storage layer"
git commit -m "fix: Resolve objdump path detection on macOS"
git commit -m "docs: Update ARCHITECTURE.md with new diagrams"
```

---

## 🐛 バグ報告・機能リクエスト

### Issueの作成

1. https://github.com/capybara-works/EVOL/issues/new にアクセス
2. 適切なテンプレートを選択（バグ報告 or 機能リクエスト）
3. 必要な情報を記入して作成

### バグ報告に含めるべき情報

- EVOL バージョン
- Python バージョン
- OS
- 再現手順
- 期待される動作
- 実際の動作
- エラーメッセージ（あれば）

---

## 📊 リポジトリ統計

公開後、以下のバッジをREADME.mdに追加することを検討:

```markdown
![GitHub Stars](https://img.shields.io/github/stars/capybara-works/EVOL?style=social)
![GitHub Issues](https://img.shields.io/github/issues/capybara-works/EVOL)
![GitHub License](https://img.shields.io/github/license/capybara-works/EVOL)
```

---

## ✅ チェックリスト

公開前の最終確認:

- [ ] README.mdのURLが正しい（`capybara-works/EVOL`）
- [ ] .gitignoreが適切（.env, *.dbなど）
- [ ] LICENSEファイルが存在する
- [ ] ARCHITECTURE.mdが最新
- [ ] 機密情報（トークンなど）がコミットされていない
- [ ] pyproject.tomlのメタデータが正確
- [ ] すべての機能が動作することを確認

公開後の確認:

- [ ] GitHubで正しく表示されている
- [ ] Clone & インストールが動作する
- [ ] Topics/Tagsが設定されている
- [ ] GitHub Pagesまたはドキュメントサイトの設定（オプション）

---

## 📝 メンテナンス

### 定期的なタスク

- 週次: Issueの確認とトリアージ
- 月次: 依存関係の更新チェック
- 四半期: ロードマップの見直し

### セキュリティ

- Dependabotを有効化（自動的に有効になる）
- Security alertsに注意
- 定期的な依存関係の更新

---

## 🤝 コントリビューター

コントリビューションを歓迎します！詳細はCONTRIBUTING.md（作成予定）を参照してください。

---

**Note**: このドキュメントは初回公開時のガイドです。プロジェクトの成長に応じて更新してください。
