"""ページモデル"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Page:
    """ページを表すモデル"""

    id: int | None = None
    slug: str = ""  # ファイル名（拡張子なし）
    title: str = ""
    file_path: Path | None = None
    metadata_type: str = "default"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)  # カスタムメタデータ
    tags: list[str] = field(default_factory=list)
    content: str = ""  # マークダウン本文

    def __post_init__(self) -> None:
        """初期化後の処理"""
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = datetime.now()

    @property
    def markdown_path(self) -> Path:
        """マークダウンファイルのパスを取得"""
        if self.file_path:
            return self.file_path
        return Path(f"{self.slug}.md")
