"""ファイルシステムストレージ"""

from datetime import datetime
from pathlib import Path
from typing import Any

from notenest.core.metadata import MetadataParser
from notenest.core.page import Page


class FileStore:
    """ファイルシステム操作"""

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = workspace_path
        self.pages_dir = workspace_path / "pages"
        self.config_dir = workspace_path / ".notenest"

        # ディレクトリ作成
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_page_file(self, page: Page) -> Path:
        """ページをマークダウンファイルとして保存"""
        # ファイルパス決定
        if page.file_path:
            file_path = page.file_path
        else:
            file_path = self.pages_dir / f"{page.slug}.md"

        # メタデータ準備
        metadata: dict[str, Any] = {
            "title": page.title,
            "tags": page.tags,
            "created": page.created_at.isoformat()
            if page.created_at
            else datetime.now().isoformat(),
            "updated": page.updated_at.isoformat()
            if page.updated_at
            else datetime.now().isoformat(),
            "metadata_type": page.metadata_type,
        }

        # カスタムメタデータを追加
        if page.metadata:
            metadata["custom_fields"] = page.metadata

        # Frontmatter付きマークダウン生成
        markdown_content = MetadataParser.serialize(metadata, page.content)

        # ファイル書き込み
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(markdown_content, encoding="utf-8")

        return file_path

    def load_page_file(self, file_path: Path) -> Page:
        """マークダウンファイルからページを読み込み"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # ファイル読み込み
        content = file_path.read_text(encoding="utf-8")

        # Frontmatter解析
        metadata, body = MetadataParser.parse(content)

        # Pageオブジェクト作成
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
            file_path=file_path,
            metadata_type=metadata_type,
            created_at=created_at,
            updated_at=updated_at,
            metadata=custom_fields,
            tags=tags,
            content=body,
        )

    def delete_page_file(self, file_path: Path) -> None:
        """マークダウンファイルを削除"""
        if file_path.exists():
            file_path.unlink()

    def list_page_files(self) -> list[Path]:
        """全ページファイルをリスト"""
        return list(self.pages_dir.glob("**/*.md"))

    def get_db_path(self) -> Path:
        """データベースファイルのパス"""
        return self.config_dir / "notenest.db"
