"""Pydantic models for API"""

from datetime import datetime

from pydantic import BaseModel, Field


class PageBase(BaseModel):
    """ページの基本情報"""

    title: str
    content: str
    metadata: dict[str, object] = Field(default_factory=dict)


class PageCreate(PageBase):
    """ページ作成リクエスト"""

    slug: str | None = None


class PageUpdate(BaseModel):
    """ページ更新リクエスト"""

    title: str | None = None
    content: str | None = None
    metadata: dict[str, object] | None = None


class PageResponse(PageBase):
    """ページレスポンス"""

    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    tags: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class PageListResponse(BaseModel):
    """ページ一覧レスポンス"""

    pages: list[PageResponse]
    total: int


class TagResponse(BaseModel):
    """タグレスポンス"""

    name: str
    count: int


class SearchQuery(BaseModel):
    """検索クエリ"""

    q: str | None = None
    tags: list[str] | None = None
    metadata_type: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = 50
    offset: int = 0


class PluginResponse(BaseModel):
    """プラグインレスポンス"""

    name: str
    version: str
    description: str
    metadata_type: str | None = None


class ErrorResponse(BaseModel):
    """エラーレスポンス"""

    detail: str
