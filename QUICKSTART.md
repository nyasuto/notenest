# NoteNest クイックスタートガイド

## インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd notenest

# 仮想環境作成と依存関係インストール
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## 起動

```bash
# デモデータで試す
notenest demo

# 自分のワークスペースで使う
notenest /path/to/your/workspace
```

## キーボードショートカット

| キー | 機能 |
|------|------|
| `n` | 新規ページ作成 |
| `e` | ページ編集（$EDITORで開く） |
| `d` | ページ削除 |
| `s` | 検索にフォーカス |
| `t` | タグ一覧表示 |
| `b` | バックリンク表示 |
| `r` | リフレッシュ |
| `q` / `Ctrl+C` | 終了 |

## ページの作成

手動でマークダウンファイルを作成：

```bash
# workspace/pages/my-note.md
cat > pages/my-note.md << 'EOF'
---
title: My First Note
tags: [test, example]
---

# My First Note

This is my first note in NoteNest!

Link to [[another-page]] using Wiki Links.
EOF
```

TUIで`r`キーを押してリフレッシュすると反映されます。

## Wiki Link記法

- `[[page-slug]]` - 基本形式
- `[[表示名|page-slug]]` - 表示名を指定

## テスト実行

```bash
pytest
```

## Phase 1実装完了

以下の機能が実装されています：

✅ マークダウンファイル管理（作成、編集、削除、プレビュー）
✅ Wiki Link（双方向リンク、バックリンク、リンク切れ検出）
✅ タグ管理（複数タグ、タグ一覧、タグフィルタリング）
✅ 全文検索（SQLite FTS5）
✅ ハイブリッドストレージ（ファイル + SQLite）
✅ TUI（Textual）
✅ 外部エディタ統合
✅ テストコード

## 次のステップ

Phase 2ではプラグインシステムと拡張機能を実装します。
詳細は issue #2 を参照してください。
