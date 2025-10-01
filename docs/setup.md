# NoteNest セットアップガイド

## 前提条件

- Python 3.11以上
- uv（推奨）または pip

## インストール

### uvを使用（推奨）

```bash
# uvのインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトディレクトリに移動
cd notenest

# 依存関係のインストール
uv pip install -e ".[dev]"
```

### pipを使用

```bash
cd notenest
pip install -e ".[dev]"
```

## 使い方

### TUIアプリの起動

```bash
# カレントディレクトリをワークスペースとして起動
notenest

# または特定のディレクトリを指定
notenest /path/to/workspace
```

### キーボードショートカット

- `n`: 新規ページ作成
- `e`: 選択中のページを編集（$EDITORで開く）
- `d`: ページ削除
- `s`: 検索にフォーカス
- `t`: タグ一覧表示
- `b`: バックリンク表示
- `r`: リフレッシュ
- `q` / `Ctrl+C`: 終了

### 検索

検索ボックスに文字を入力すると、全文検索が実行されます。

## 開発

### テストの実行

```bash
pytest
```

### コードフォーマット

```bash
ruff format src/ tests/
```

### リント

```bash
ruff check src/ tests/
```

### 型チェック

```bash
mypy src/
```

## ディレクトリ構造

ワークスペース内には以下の構造が作成されます：

```
workspace/
├── pages/           # マークダウンファイル
│   ├── page1.md
│   └── page2.md
└── .notenest/       # 設定・データベース
    └── notenest.db  # SQLiteデータベース
```
