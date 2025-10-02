"""Pages API routes"""

from fastapi import APIRouter, HTTPException

from notenest.core.page import Page
from notenest.core.repository import Repository
from web.api.dependencies import get_repository
from web.api.models import PageCreate, PageListResponse, PageResponse, PageUpdate

router = APIRouter()


def _page_to_response(page: Page) -> PageResponse:
    """PageモデルをPageResponseに変換"""
    return PageResponse(
        id=page.id,
        slug=page.slug,
        title=page.title,
        content=page.content,
        metadata=page.metadata,
        created_at=page.created_at,
        updated_at=page.updated_at,
        tags=page.tags,
    )


@router.get("", response_model=PageListResponse)
async def list_pages(limit: int = 50, offset: int = 0) -> PageListResponse:
    """ページ一覧を取得"""
    repo: Repository = get_repository()
    all_pages = repo.list_pages()

    # ページネーション
    total = len(all_pages)
    pages = all_pages[offset : offset + limit]

    return PageListResponse(
        pages=[_page_to_response(p) for p in pages],
        total=total,
    )


@router.get("/{slug}", response_model=PageResponse)
async def get_page(slug: str) -> PageResponse:
    """ページを取得"""
    repo: Repository = get_repository()
    page = repo.get_page(slug)

    if not page:
        raise HTTPException(status_code=404, detail=f"Page '{slug}' not found")

    return _page_to_response(page)


@router.post("", response_model=PageResponse, status_code=201)
async def create_page(page_data: PageCreate) -> PageResponse:
    """ページを作成"""
    repo: Repository = get_repository()

    # slugが指定されていない場合はtitleから生成
    slug = page_data.slug
    if not slug:
        slug = page_data.title.lower().replace(" ", "-")

    # 既存ページチェック
    existing = repo.get_page(slug)
    if existing:
        raise HTTPException(status_code=409, detail=f"Page '{slug}' already exists")

    # ページ作成
    created_page = repo.create_page(
        slug=slug,
        title=page_data.title,
        content=page_data.content,
        metadata=page_data.metadata,
    )

    return _page_to_response(created_page)


@router.put("/{slug}", response_model=PageResponse)
async def update_page(slug: str, page_data: PageUpdate) -> PageResponse:
    """ページを更新"""
    repo: Repository = get_repository()

    # 既存ページ取得
    existing = repo.get_page(slug)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Page '{slug}' not found")

    # 更新
    repo.update_page(
        slug=slug,
        title=page_data.title,
        content=page_data.content,
        tags=None,
        metadata=page_data.metadata,
    )
    updated_page = repo.get_page(slug)

    if not updated_page:
        raise HTTPException(status_code=500, detail="Failed to update page")

    return _page_to_response(updated_page)


@router.delete("/{slug}", status_code=204)
async def delete_page(slug: str) -> None:
    """ページを削除"""
    repo: Repository = get_repository()

    existing = repo.get_page(slug)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Page '{slug}' not found")

    repo.delete_page(slug)


@router.get("/{slug}/backlinks", response_model=PageListResponse)
async def get_backlinks(slug: str) -> PageListResponse:
    """バックリンクを取得"""
    repo: Repository = get_repository()

    # ページ存在確認
    page = repo.get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail=f"Page '{slug}' not found")

    # バックリンク取得
    backlinks = repo.get_backlinks(slug)

    # リンクからページを取得
    backlink_pages = []
    for link in backlinks:
        source_page = repo.get_page(link.source_slug)
        if source_page:
            backlink_pages.append(source_page)

    return PageListResponse(
        pages=[_page_to_response(p) for p in backlink_pages],
        total=len(backlink_pages),
    )
