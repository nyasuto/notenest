"""リポジトリのテスト"""

import tempfile
from pathlib import Path

import pytest

from notenest.core.repository import Repository


@pytest.fixture
def temp_workspace():
    """一時ワークスペース"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_create_and_get_page(temp_workspace):
    """ページ作成と取得のテスト"""
    repo = Repository(temp_workspace)

    # ページ作成
    page = repo.create_page(
        slug="test-page", title="Test Page", content="# Hello\n\nThis is a test.", tags=["test"]
    )

    assert page.id is not None
    assert page.slug == "test-page"
    assert page.title == "Test Page"

    # ページ取得
    retrieved = repo.get_page("test-page")
    assert retrieved is not None
    assert retrieved.slug == "test-page"
    assert retrieved.title == "Test Page"
    assert "Hello" in retrieved.content
    assert "test" in retrieved.tags

    repo.close()


def test_update_page(temp_workspace):
    """ページ更新のテスト"""
    repo = Repository(temp_workspace)

    # ページ作成
    repo.create_page(slug="test", title="Original", content="Original content")

    # 更新
    updated = repo.update_page(slug="test", title="Updated", content="Updated content")

    assert updated is not None
    assert updated.title == "Updated"
    assert "Updated content" in updated.content

    repo.close()


def test_wiki_links(temp_workspace):
    """Wiki Linkのテスト"""
    repo = Repository(temp_workspace)

    # ページ作成（リンクを含む）
    repo.create_page(
        slug="page1",
        title="Page 1",
        content="This links to [[page2]] and [[page3]].",
    )

    repo.create_page(slug="page2", title="Page 2", content="Content")

    # 発リンク取得
    outgoing = repo.get_outgoing_links("page1")
    assert len(outgoing) == 2
    assert any(link.target_slug == "page2" for link in outgoing)
    assert any(link.target_slug == "page3" for link in outgoing)

    # バックリンク取得
    backlinks = repo.get_backlinks("page2")
    assert len(backlinks) == 1
    assert backlinks[0].source_slug == "page1"

    # リンク切れ検出
    broken = repo.get_broken_links()
    assert len(broken) == 1
    assert broken[0].target_slug == "page3"

    repo.close()


def test_tags(temp_workspace):
    """タグのテスト"""
    repo = Repository(temp_workspace)

    # タグ付きページ作成
    repo.create_page(slug="page1", title="Page 1", content="Content", tags=["python", "test"])
    repo.create_page(slug="page2", title="Page 2", content="Content", tags=["python"])

    # 全タグ取得
    all_tags = repo.get_all_tags()
    assert len(all_tags) == 2

    python_tag = next(tag for tag in all_tags if tag.name == "python")
    assert python_tag.page_count == 2

    # タグでページ検索
    python_pages = repo.get_pages_by_tag("python")
    assert len(python_pages) == 2

    repo.close()
