"""インポート機能"""

import json
from datetime import datetime
from pathlib import Path

from notenest.core.metadata import MetadataParser
from notenest.core.page import Page


class Importer:
    """ページのインポート機能"""

    @staticmethod
    def import_from_markdown(file_path: Path) -> Page:
        """
        マークダウンファイルからページをインポート

        Args:
            file_path: インポート元ファイルパス

        Returns:
            Page: インポートされたページ
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        metadata, body = MetadataParser.parse(content)

        slug = file_path.stem
        title = metadata.get("title", slug)
        tags = metadata.get("tags", [])
        metadata_type = metadata.get("metadata_type", "default")
        custom_fields = metadata.get("custom_fields", {})

        # 日時パース
        created_at = None
        if "created" in metadata:
            try:
                created_at = datetime.fromisoformat(metadata["created"])
            except (ValueError, TypeError):
                pass

        updated_at = None
        if "updated" in metadata:
            try:
                updated_at = datetime.fromisoformat(metadata["updated"])
            except (ValueError, TypeError):
                pass

        return Page(
            slug=slug,
            title=title,
            content=body,
            tags=tags,
            metadata_type=metadata_type,
            metadata=custom_fields,
            created_at=created_at,
            updated_at=updated_at,
            file_path=file_path,
        )

    @staticmethod
    def import_from_json(file_path: Path) -> Page:
        """
        JSONファイルからページをインポート

        Args:
            file_path: インポート元ファイルパス

        Returns:
            Page: インポートされたページ
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        json_str = file_path.read_text(encoding="utf-8")
        data = json.loads(json_str)

        # 日時パース
        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass

        updated_at = None
        if data.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except (ValueError, TypeError):
                pass

        return Page(
            slug=data.get("slug", file_path.stem),
            title=data.get("title", "Untitled"),
            content=data.get("content", ""),
            tags=data.get("tags", []),
            metadata_type=data.get("metadata_type", "default"),
            metadata=data.get("metadata", {}),
            created_at=created_at,
            updated_at=updated_at,
        )

    @staticmethod
    def import_all_from_json(file_path: Path) -> list[Page]:
        """
        JSON形式のエクスポートファイルから全ページをインポート

        Args:
            file_path: インポート元ファイルパス

        Returns:
            list: インポートされたページリスト
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        json_str = file_path.read_text(encoding="utf-8")
        data = json.loads(json_str)

        pages = []
        for page_data in data.get("pages", []):
            # 日時パース
            created_at = None
            if page_data.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(page_data["created_at"])
                except (ValueError, TypeError):
                    pass

            updated_at = None
            if page_data.get("updated_at"):
                try:
                    updated_at = datetime.fromisoformat(page_data["updated_at"])
                except (ValueError, TypeError):
                    pass

            page = Page(
                slug=page_data.get("slug", "untitled"),
                title=page_data.get("title", "Untitled"),
                content=page_data.get("content", ""),
                tags=page_data.get("tags", []),
                metadata_type=page_data.get("metadata_type", "default"),
                metadata=page_data.get("metadata", {}),
                created_at=created_at,
                updated_at=updated_at,
            )
            pages.append(page)

        return pages

    @staticmethod
    def import_from_obsidian(file_path: Path) -> Page:
        """
        Obsidian形式のマークダウンファイルからインポート

        Args:
            file_path: インポート元ファイルパス

        Returns:
            Page: インポートされたページ

        Note:
            Obsidian形式は基本的に標準マークダウンと同じだが、
            タグの表記（#tag）やリンクの形式（[[link]]）が異なる場合がある
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")

        # Obsidian形式のタグを抽出（#tagの形式）
        import re

        obsidian_tags = re.findall(r"#([a-zA-Z0-9_\-]+)", content)

        # Frontmatter解析
        metadata, body = MetadataParser.parse(content)

        slug = file_path.stem
        title = metadata.get("title", slug)

        # Frontmatterのtagsとインラインタグを統合
        tags = list(set(metadata.get("tags", []) + obsidian_tags))

        metadata_type = metadata.get("metadata_type", "default")
        custom_fields = metadata.get("custom_fields", {})

        return Page(
            slug=slug,
            title=title,
            content=body,
            tags=tags,
            metadata_type=metadata_type,
            metadata=custom_fields,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            file_path=file_path,
        )

    @staticmethod
    def import_directory(directory: Path, format: str = "markdown") -> list[Page]:
        """
        ディレクトリから全ファイルをインポート

        Args:
            directory: インポート元ディレクトリ
            format: フォーマット（markdown, json, obsidian）

        Returns:
            list: インポートされたページリスト
        """
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Directory not found: {directory}")

        pages = []

        if format == "markdown":
            for md_file in directory.glob("**/*.md"):
                try:
                    page = Importer.import_from_markdown(md_file)
                    pages.append(page)
                except Exception as e:
                    print(f"Failed to import {md_file}: {e}")

        elif format == "obsidian":
            for md_file in directory.glob("**/*.md"):
                try:
                    page = Importer.import_from_obsidian(md_file)
                    pages.append(page)
                except Exception as e:
                    print(f"Failed to import {md_file}: {e}")

        elif format == "json":
            for json_file in directory.glob("**/*.json"):
                try:
                    page = Importer.import_from_json(json_file)
                    pages.append(page)
                except Exception as e:
                    print(f"Failed to import {json_file}: {e}")

        return pages
