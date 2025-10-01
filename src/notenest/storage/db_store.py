"""SQLiteストレージ"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from notenest.core.link import Link
from notenest.core.page import Page
from notenest.core.tag import Tag


class DBStore:
    """SQLiteデータベース操作"""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        """データベース接続"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        # 外部キー制約を有効化（ON DELETE CASCADEを機能させるため）
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._initialize_schema()

    def close(self) -> None:
        """データベース切断"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _initialize_schema(self) -> None:
        """スキーマ初期化"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()

        # ページテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL,
                metadata_type TEXT DEFAULT 'default',
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                metadata_json TEXT
            )
        """)

        # 全文検索テーブル（FTS5）
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                slug, title, content, tags,
                tokenize='porter unicode61'
            )
        """)

        # リンクテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_page_id INTEGER NOT NULL,
                target_slug TEXT NOT NULL,
                link_type TEXT DEFAULT 'wiki',
                FOREIGN KEY (source_page_id) REFERENCES pages(id) ON DELETE CASCADE
            )
        """)

        # タグテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)

        # ページ-タグ関連テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_tags (
                page_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (page_id, tag_id),
                FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        # インデックス作成
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_page_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_page_tags_page ON page_tags(page_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_page_tags_tag ON page_tags(tag_id)")

        self.conn.commit()

    # ========== ページ操作 ==========

    def save_page(self, page: Page) -> int:
        """ページを保存（新規作成または更新）"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        metadata_json = json.dumps(page.metadata, ensure_ascii=False) if page.metadata else None

        if page.id:
            # 更新
            cursor.execute(
                """
                UPDATE pages
                SET slug = ?, title = ?, file_path = ?, metadata_type = ?,
                    updated_at = ?, metadata_json = ?
                WHERE id = ?
            """,
                (
                    page.slug,
                    page.title,
                    str(page.file_path) if page.file_path else "",
                    page.metadata_type,
                    (page.updated_at or datetime.now()).isoformat(),
                    metadata_json,
                    page.id,
                ),
            )
            page_id = page.id
        else:
            # 新規作成
            cursor.execute(
                """
                INSERT INTO pages (slug, title, file_path, metadata_type, created_at, updated_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    page.slug,
                    page.title,
                    str(page.file_path) if page.file_path else "",
                    page.metadata_type,
                    (page.created_at or datetime.now()).isoformat(),
                    (page.updated_at or datetime.now()).isoformat(),
                    metadata_json,
                ),
            )
            assert cursor.lastrowid is not None
            page_id = cursor.lastrowid

        self.conn.commit()
        return page_id

    def get_page_by_id(self, page_id: int) -> Page | None:
        """IDでページを取得"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pages WHERE id = ?", (page_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_page(row)

    def get_page_by_slug(self, slug: str) -> Page | None:
        """slugでページを取得"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pages WHERE slug = ?", (slug,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_page(row)

    def get_all_pages(self) -> list[Page]:
        """全ページを取得"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pages ORDER BY updated_at DESC")
        rows = cursor.fetchall()

        return [self._row_to_page(row) for row in rows]

    def delete_page(self, page_id: int) -> None:
        """ページを削除"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM pages WHERE id = ?", (page_id,))
        self.conn.commit()

    def _row_to_page(self, row: sqlite3.Row) -> Page:
        """行データをPageオブジェクトに変換"""
        metadata = json.loads(row["metadata_json"]) if row["metadata_json"] else {}

        return Page(
            id=row["id"],
            slug=row["slug"],
            title=row["title"],
            file_path=Path(row["file_path"]) if row["file_path"] else None,
            metadata_type=row["metadata_type"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metadata=metadata,
        )

    # ========== リンク操作 ==========

    def save_links(self, source_page_id: int, target_slugs: list[str]) -> None:
        """ページのリンクを保存（既存リンクは削除して再作成）"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()

        # 既存リンク削除
        cursor.execute("DELETE FROM links WHERE source_page_id = ?", (source_page_id,))

        # 新規リンク追加
        for target_slug in target_slugs:
            cursor.execute(
                "INSERT INTO links (source_page_id, target_slug, link_type) VALUES (?, ?, ?)",
                (source_page_id, target_slug, "wiki"),
            )

        self.conn.commit()

    def get_outgoing_links(self, page_id: int) -> list[Link]:
        """ページからの発リンク（outgoing links）を取得"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT l.*, p.slug as source_slug
            FROM links l
            JOIN pages p ON l.source_page_id = p.id
            WHERE l.source_page_id = ?
        """,
            (page_id,),
        )
        rows = cursor.fetchall()

        return [
            Link(
                id=row["id"],
                source_page_id=row["source_page_id"],
                source_slug=row["source_slug"],
                target_slug=row["target_slug"],
                link_type=row["link_type"],
            )
            for row in rows
        ]

    def get_backlinks(self, slug: str) -> list[Link]:
        """ページへのバックリンク（incoming links）を取得"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT l.*, p.slug as source_slug
            FROM links l
            JOIN pages p ON l.source_page_id = p.id
            WHERE l.target_slug = ?
        """,
            (slug,),
        )
        rows = cursor.fetchall()

        return [
            Link(
                id=row["id"],
                source_page_id=row["source_page_id"],
                source_slug=row["source_slug"],
                target_slug=row["target_slug"],
                link_type=row["link_type"],
            )
            for row in rows
        ]

    # ========== タグ操作 ==========

    def get_or_create_tag(self, tag_name: str) -> int:
        """タグを取得または作成"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()

        # 既存タグを検索
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        row = cursor.fetchone()

        if row:
            return int(row["id"])

        # 新規作成
        cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
        self.conn.commit()
        assert cursor.lastrowid is not None
        return cursor.lastrowid

    def save_page_tags(self, page_id: int, tag_names: list[str]) -> None:
        """ページのタグを保存（既存タグは削除して再作成）"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()

        # 既存タグ関連削除
        cursor.execute("DELETE FROM page_tags WHERE page_id = ?", (page_id,))

        # 新規タグ追加
        for tag_name in tag_names:
            tag_id = self.get_or_create_tag(tag_name)
            cursor.execute(
                "INSERT INTO page_tags (page_id, tag_id) VALUES (?, ?)", (page_id, tag_id)
            )

        self.conn.commit()

    def get_page_tags(self, page_id: int) -> list[Tag]:
        """ページのタグを取得"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT t.id, t.name
            FROM tags t
            JOIN page_tags pt ON t.id = pt.tag_id
            WHERE pt.page_id = ?
        """,
            (page_id,),
        )
        rows = cursor.fetchall()

        return [Tag(id=row["id"], name=row["name"]) for row in rows]

    def get_all_tags(self) -> list[Tag]:
        """全タグを取得（使用回数付き）"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, t.name, COUNT(pt.page_id) as page_count
            FROM tags t
            LEFT JOIN page_tags pt ON t.id = pt.tag_id
            GROUP BY t.id, t.name
            ORDER BY page_count DESC, t.name
        """)
        rows = cursor.fetchall()

        return [Tag(id=row["id"], name=row["name"], page_count=row["page_count"]) for row in rows]

    def get_pages_by_tag(self, tag_name: str) -> list[Page]:
        """タグでページを検索"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT p.*
            FROM pages p
            JOIN page_tags pt ON p.id = pt.page_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY p.updated_at DESC
        """,
            (tag_name,),
        )
        rows = cursor.fetchall()

        return [self._row_to_page(row) for row in rows]

    # ========== 検索操作 ==========

    def index_page_for_search(
        self, page_id: int, slug: str, title: str, content: str, tags: list[str]
    ) -> None:
        """ページを全文検索インデックスに追加"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()

        # 既存インデックス削除
        cursor.execute("DELETE FROM pages_fts WHERE rowid = ?", (page_id,))

        # 新規インデックス追加
        tags_str = " ".join(tags)
        cursor.execute(
            "INSERT INTO pages_fts (rowid, slug, title, content, tags) VALUES (?, ?, ?, ?, ?)",
            (page_id, slug, title, content, tags_str),
        )

        self.conn.commit()

    def search_pages(self, query: str) -> list[Page]:
        """全文検索"""
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT p.*
            FROM pages p
            JOIN pages_fts fts ON p.id = fts.rowid
            WHERE pages_fts MATCH ?
            ORDER BY rank
        """,
            (query,),
        )
        rows = cursor.fetchall()

        return [self._row_to_page(row) for row in rows]
