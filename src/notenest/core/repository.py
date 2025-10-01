"""リポジトリ - ストレージ層とコア機能を統合"""

from datetime import datetime
from pathlib import Path
from typing import Any

from notenest.core.link import Link
from notenest.core.metadata import WikiLinkParser
from notenest.core.page import Page
from notenest.core.tag import Tag
from notenest.storage.db_store import DBStore
from notenest.storage.file_store import FileStore


class Repository:
    """ページ、リンク、タグの統合管理"""

    def __init__(self, workspace_path: Path) -> None:
        self.file_store = FileStore(workspace_path)
        self.db_store = DBStore(self.file_store.get_db_path())
        self.db_store.connect()

    def close(self) -> None:
        """リソースのクリーンアップ"""
        self.db_store.close()

    # ========== ページ操作 ==========

    def create_page(
        self,
        slug: str,
        title: str,
        content: str = "",
        tags: list[str] | None = None,
        metadata_type: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> Page:
        """ページを作成"""
        page = Page(
            slug=slug,
            title=title,
            content=content,
            tags=tags or [],
            metadata_type=metadata_type,
            metadata=metadata or {},
        )

        # ファイル保存
        file_path = self.file_store.save_page_file(page)
        page.file_path = file_path

        # DB保存
        page_id = self.db_store.save_page(page)
        page.id = page_id

        # タグ保存
        if page.tags:
            self.db_store.save_page_tags(page_id, page.tags)

        # リンク解析・保存
        links = WikiLinkParser.extract_links(content)
        if links:
            self.db_store.save_links(page_id, links)

        # 検索インデックス更新
        self.db_store.index_page_for_search(page_id, slug, title, content, page.tags)

        return page

    def get_page(self, slug: str) -> Page | None:
        """ページを取得"""
        page = self.db_store.get_page_by_slug(slug)
        if not page:
            return None

        # ファイルからコンテンツ読み込み
        if page.file_path and page.file_path.exists():
            file_page = self.file_store.load_page_file(page.file_path)
            page.content = file_page.content

        # タグ読み込み
        if page.id:
            tags = self.db_store.get_page_tags(page.id)
            page.tags = [tag.name for tag in tags]

        return page

    def update_page(
        self,
        slug: str,
        title: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Page | None:
        """ページを更新"""
        page = self.get_page(slug)
        if not page or not page.id:
            return None

        # 更新
        if title is not None:
            page.title = title
        if content is not None:
            page.content = content
        if tags is not None:
            page.tags = tags
        if metadata is not None:
            page.metadata.update(metadata)

        page.updated_at = datetime.now()

        # ファイル保存
        self.file_store.save_page_file(page)

        # DB更新
        self.db_store.save_page(page)

        # タグ更新
        self.db_store.save_page_tags(page.id, page.tags)

        # リンク更新
        links = WikiLinkParser.extract_links(page.content)
        self.db_store.save_links(page.id, links)

        # 検索インデックス更新
        self.db_store.index_page_for_search(page.id, page.slug, page.title, page.content, page.tags)

        return page

    def delete_page(self, slug: str) -> bool:
        """ページを削除"""
        page = self.db_store.get_page_by_slug(slug)
        if not page or not page.id:
            return False

        # ファイル削除
        if page.file_path and page.file_path.exists():
            self.file_store.delete_page_file(page.file_path)

        # DB削除（カスケードでリンク・タグも削除）
        self.db_store.delete_page(page.id)

        return True

    def list_pages(self) -> list[Page]:
        """全ページをリスト"""
        pages = self.db_store.get_all_pages()

        # 各ページのタグを読み込み
        for page in pages:
            if page.id:
                tags = self.db_store.get_page_tags(page.id)
                page.tags = [tag.name for tag in tags]

        return pages

    def sync_from_files(self) -> None:
        """ファイルシステムからDBを同期"""
        # 全マークダウンファイルを走査
        for file_path in self.file_store.list_page_files():
            try:
                page = self.file_store.load_page_file(file_path)

                # DB に存在するか確認
                existing = self.db_store.get_page_by_slug(page.slug)

                if existing:
                    # 更新
                    page.id = existing.id
                    self.update_page(
                        page.slug,
                        title=page.title,
                        content=page.content,
                        tags=page.tags,
                        metadata=page.metadata,
                    )
                else:
                    # 新規作成
                    self.create_page(
                        slug=page.slug,
                        title=page.title,
                        content=page.content,
                        tags=page.tags,
                        metadata_type=page.metadata_type,
                        metadata=page.metadata,
                    )
            except Exception as e:
                print(f"Error syncing {file_path}: {e}")

    # ========== リンク操作 ==========

    def get_outgoing_links(self, slug: str) -> list[Link]:
        """ページからの発リンクを取得"""
        page = self.db_store.get_page_by_slug(slug)
        if not page or not page.id:
            return []

        return self.db_store.get_outgoing_links(page.id)

    def get_backlinks(self, slug: str) -> list[Link]:
        """ページへのバックリンクを取得"""
        return self.db_store.get_backlinks(slug)

    def get_broken_links(self) -> list[Link]:
        """リンク切れを取得"""
        all_pages = self.db_store.get_all_pages()
        existing_slugs = {page.slug for page in all_pages}

        broken_links = []
        for page in all_pages:
            if not page.id:
                continue
            outgoing = self.db_store.get_outgoing_links(page.id)
            for link in outgoing:
                if link.target_slug not in existing_slugs:
                    broken_links.append(link)

        return broken_links

    # ========== タグ操作 ==========

    def get_all_tags(self) -> list[Tag]:
        """全タグを取得"""
        return self.db_store.get_all_tags()

    def get_pages_by_tag(self, tag_name: str) -> list[Page]:
        """タグでページを検索"""
        pages = self.db_store.get_pages_by_tag(tag_name)

        # 各ページのタグを読み込み
        for page in pages:
            if page.id:
                tags = self.db_store.get_page_tags(page.id)
                page.tags = [tag.name for tag in tags]

        return pages

    # ========== 検索操作 ==========

    def search_pages(self, query: str) -> list[Page]:
        """全文検索"""
        pages = self.db_store.search_pages(query)

        # 各ページのタグを読み込み
        for page in pages:
            if page.id:
                tags = self.db_store.get_page_tags(page.id)
                page.tags = [tag.name for tag in tags]

        return pages
