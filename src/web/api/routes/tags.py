"""Tags API routes"""

from fastapi import APIRouter

from notenest.core.repository import Repository
from web.api.main import get_repository
from web.api.models import PageListResponse, TagResponse
from web.api.routes.pages import _page_to_response

router = APIRouter()


@router.get("", response_model=list[TagResponse])
async def list_tags() -> list[TagResponse]:
    """タグ一覧を取得"""
    repo: Repository = get_repository()
    tags = repo.get_all_tags()

    # タグごとのページ数をカウント
    tag_counts = []
    for tag in tags:
        pages = repo.get_pages_by_tag(tag.name)
        tag_counts.append(TagResponse(name=tag.name, count=len(pages)))

    return tag_counts


@router.get("/{tag}/pages", response_model=PageListResponse)
async def get_pages_by_tag(tag: str) -> PageListResponse:
    """特定タグのページ一覧を取得"""
    repo: Repository = get_repository()
    pages = repo.get_pages_by_tag(tag)

    return PageListResponse(
        pages=[_page_to_response(p) for p in pages],
        total=len(pages),
    )
