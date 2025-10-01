"""高度な検索機能のテスト"""

from datetime import datetime, timedelta

from notenest.core.page import Page
from notenest.core.search import AdvancedSearch, DateRangeFilter


def test_filter_by_date_range():
    """日付範囲フィルタのテスト"""
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    pages = [
        Page(slug="p1", title="Page 1", updated_at=yesterday),
        Page(slug="p2", title="Page 2", updated_at=now),
        Page(slug="p3", title="Page 3", updated_at=tomorrow),
    ]

    # 今日以降
    date_range = DateRangeFilter(start_date=now, end_date=None)
    filtered = AdvancedSearch.filter_by_date_range(pages, date_range)
    assert len(filtered) == 2  # p2, p3

    # 昨日から今日
    date_range = DateRangeFilter(start_date=yesterday, end_date=now)
    filtered = AdvancedSearch.filter_by_date_range(pages, date_range)
    assert len(filtered) == 2  # p1, p2


def test_filter_by_metadata_field():
    """メタデータフィールドフィルタのテスト"""
    pages = [
        Page(slug="p1", title="Page 1", metadata={"difficulty": "easy"}),
        Page(slug="p2", title="Page 2", metadata={"difficulty": "hard"}),
        Page(slug="p3", title="Page 3", metadata={"rating": 4.5}),
    ]

    # 文字列フィルタ
    filtered = AdvancedSearch.filter_by_metadata_field(pages, "difficulty", "easy")
    assert len(filtered) == 1
    assert filtered[0].slug == "p1"

    # 数値フィルタ
    filtered = AdvancedSearch.filter_by_metadata_field(pages, "rating", 4.5)
    assert len(filtered) == 1
    assert filtered[0].slug == "p3"


def test_filter_by_tags():
    """タグフィルタのテスト"""
    pages = [
        Page(slug="p1", title="Page 1", tags=["python", "tutorial"]),
        Page(slug="p2", title="Page 2", tags=["python", "advanced"]),
        Page(slug="p3", title="Page 3", tags=["rust", "tutorial"]),
    ]

    # いずれかのタグに一致
    filtered = AdvancedSearch.filter_by_tags(pages, ["python"], match_all=False)
    assert len(filtered) == 2  # p1, p2

    # 全タグに一致
    filtered = AdvancedSearch.filter_by_tags(pages, ["python", "tutorial"], match_all=True)
    assert len(filtered) == 1  # p1のみ


def test_sort_pages():
    """ページソートのテスト"""
    pages = [
        Page(slug="c", title="C Page"),
        Page(slug="a", title="A Page"),
        Page(slug="b", title="B Page"),
    ]

    # タイトルでソート
    sorted_pages = AdvancedSearch.sort_pages(pages, sort_by="title", reverse=False)
    assert sorted_pages[0].title == "A Page"
    assert sorted_pages[2].title == "C Page"

    # slugでソート
    sorted_pages = AdvancedSearch.sort_pages(pages, sort_by="slug", reverse=False)
    assert sorted_pages[0].slug == "a"
    assert sorted_pages[2].slug == "c"


def test_complex_search():
    """複合検索のテスト"""
    pages = [
        Page(
            slug="p1",
            title="Python Tutorial",
            content="Learn Python basics",
            tags=["python", "tutorial"],
            metadata_type="tutorial",
        ),
        Page(
            slug="p2",
            title="Rust Guide",
            content="Advanced Rust programming",
            tags=["rust", "advanced"],
            metadata_type="guide",
        ),
        Page(
            slug="p3",
            title="Python Advanced",
            content="Advanced Python topics",
            tags=["python", "advanced"],
            metadata_type="tutorial",
        ),
    ]

    # テキスト検索 + タグフィルタ
    result = AdvancedSearch.complex_search(
        pages, text_query="Python", tags=["tutorial"], sort_by="title"
    )
    assert len(result) == 1
    assert result[0].slug == "p1"

    # メタデータ型フィルタ
    result = AdvancedSearch.complex_search(pages, metadata_type="tutorial")
    assert len(result) == 2  # p1, p3
