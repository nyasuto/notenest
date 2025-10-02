# Web GUI for NoteNest

NoteNestのWeb GUIインターフェースです。

## 構成

### バックエンド (FastAPI)
- **場所**: `src/web/api/`
- **ポート**: 8000
- **技術**: FastAPI + Uvicorn

### フロントエンド (React)
- **場所**: `src/web/frontend/`
- **ポート**: 5173 (開発サーバー)
- **技術**: React + TypeScript + Vite + TailwindCSS

## セットアップ

### 1. バックエンドの依存関係をインストール
```bash
uv pip install -e ".[dev]"
```

### 2. フロントエンドの依存関係をインストール
```bash
make web-install
```

## 使い方

### 開発モード

#### ターミナル1: APIサーバーを起動
```bash
make web-api
```

APIは `http://localhost:8000` で起動します。

#### ターミナル2: フロントエンド開発サーバーを起動
```bash
make web-dev
```

フロントエンドは `http://localhost:5173` で起動します。

### プロダクションビルド

```bash
# フロントエンドをビルド
make web-build

# ビルドされたファイルは src/web/frontend/dist/ に生成されます
```

## API仕様

APIドキュメントは、APIサーバー起動後に以下のURLで確認できます：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 主な機能

- ページ一覧表示
- ページ詳細表示（Markdownプレビュー）
- ページ作成・編集・削除
- タグ一覧・タグ別ページ表示
- 全文検索
- プラグイン情報表示
- バックリンク表示

## 開発

### ディレクトリ構成
```
src/web/
├── api/                    # FastAPI バックエンド
│   ├── main.py            # アプリケーションエントリーポイント
│   ├── models.py          # Pydanticモデル
│   └── routes/            # APIルート
│       ├── pages.py       # ページAPI
│       ├── tags.py        # タグAPI
│       ├── search.py      # 検索API
│       └── plugins.py     # プラグインAPI
└── frontend/              # React フロントエンド
    ├── src/
    │   ├── api/           # APIクライアント
    │   ├── components/    # Reactコンポーネント
    │   ├── pages/         # ページコンポーネント
    │   └── types/         # TypeScript型定義
    └── package.json
```

### 既存のTUIとの共存

Web GUIとTUIは同じワークスペースを共有します。どちらのインターフェースからも同じデータにアクセスできます。

```bash
# TUIを起動
python -m notenest

# Web GUIを起動（別ターミナルで）
make web-api
make web-dev  # 別のターミナルで
```
