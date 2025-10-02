"""Search API routes"""

from fastapi import APIRouter

from notenest.core.repository import Repository
from notenest.core.search import AdvancedSearch
from web.api.dependencies import get_repository
from web.api.models import PageListResponse, SearchQuery
from web.api.routes.pages import _page_to_response

router = APIRouter()


@router.post("", response_model=PageListResponse)
async def search_pages(query: SearchQuery) -> PageListResponse:
    """ページを検索"""
    repo: Repository = get_repository()

    # 全ページを取得
    all_pages = repo.list_pages()

    # テキスト検索
    if query.q:
        search_results = repo.search_pages(query.q)
        # IDのセットを作成
        result_ids = {p.id for p in search_results if p.id is not None}
        # フィルタリング
        all_pages = [p for p in all_pages if p.id is not None and p.id in result_ids]

    # 高度なフィルタリング
    date_range_filter = None
    if query.start_date and query.end_date:
        date_range_filter = (query.start_date, query.end_date)

    filtered_pages = AdvancedSearch.complex_search(
        all_pages,
        text_query=None,  # 既にテキスト検索済み
        tags=query.tags,
        metadata_type=query.metadata_type,
        date_range=date_range_filter,
    )

    # ページネーション
    total = len(filtered_pages)
    pages = filtered_pages[query.offset : query.offset + query.limit]

    return PageListResponse(
        pages=[_page_to_response(p) for p in pages],
        total=total,
    )
