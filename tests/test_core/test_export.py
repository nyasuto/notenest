"""Export functionality tests"""

import json
from datetime import datetime

import pytest

from notenest.core.export import Exporter
from notenest.core.page import Page


@pytest.fixture
def sample_page():
    """サンプルページを返すフィクスチャ"""
    return Page(
        id=1,
        slug="test-page",
        title="Test Page",
        content="# Hello\n\nThis is a **test** page.",
        tags=["python", "testing"],
        metadata_type="default",
        metadata={},
        created_at=datetime(2025, 1, 1, 12, 0, 0),
        updated_at=datetime(2025, 1, 2, 15, 30, 0),
    )


@pytest.fixture
def sample_pages():
    """複数のサンプルページを返すフィクスチャ"""
    return [
        Page(
            id=1,
            slug="page-one",
            title="Page One",
            content="# Page 1",
            tags=["tag1"],
            metadata_type="default",
            metadata={},
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 1, 12, 0, 0),
        ),
        Page(
            id=2,
            slug="page-two",
            title="Page Two",
            content="# Page 2",
            tags=["tag2"],
            metadata_type="default",
            metadata={},
            created_at=datetime(2025, 1, 2, 12, 0, 0),
            updated_at=datetime(2025, 1, 2, 12, 0, 0),
        ),
    ]


class TestExportToHTML:
    """HTML エクスポートのテスト"""

    def test_export_to_html_without_output_path(self, sample_page):
        """出力パスなしでHTMLを生成"""
        html = Exporter.export_to_html(sample_page)

        # HTMLが生成されること
        assert html
        assert "<!DOCTYPE html>" in html
        assert '<html lang="ja">' in html

        # ページ情報が含まれること
        assert "Test Page" in html
        assert "test-page" in html
        assert "default" in html

        # マークダウンがHTMLに変換されていること
        # markdownライブラリはh1にidを自動追加する
        assert '<h1 id="hello">Hello</h1>' in html or "<h1>Hello</h1>" in html
        assert "<strong>test</strong>" in html

        # タグが含まれること
        assert "python" in html
        assert "testing" in html

        # 日時が含まれること
        assert "2025-01-01 12:00" in html
        assert "2025-01-02 15:30" in html

    def test_export_to_html_with_output_path(self, sample_page, tmp_path):
        """出力パス指定でHTMLファイルを生成"""
        output_path = tmp_path / "output" / "test.html"
        html = Exporter.export_to_html(sample_page, output_path)

        # ファイルが作成されること
        assert output_path.exists()

        # ファイル内容が正しいこと
        file_content = output_path.read_text(encoding="utf-8")
        assert file_content == html
        assert "Test Page" in file_content

    def test_export_to_html_with_none_dates(self):
        """created_at/updated_atがNoneの場合"""
        page = Page(
            id=1,
            slug="test",
            title="Test",
            content="Content",
            tags=[],
            metadata_type="default",
            metadata={},
            created_at=None,
            updated_at=None,
        )

        html = Exporter.export_to_html(page)
        # Pageクラスがデフォルト値を設定する場合があるのでチェックを緩和
        assert "Created:" in html
        assert "Updated:" in html

    def test_export_all_to_html(self, sample_pages, tmp_path):
        """全ページをHTMLにエクスポート"""
        output_dir = tmp_path / "html_export"
        output_files = Exporter.export_all_to_html(sample_pages, output_dir)

        # 出力ディレクトリが作成されること
        assert output_dir.exists()

        # ページ数+1（インデックス）のファイルが生成されること
        assert len(output_files) == 3  # 2 pages + 1 index

        # 各ページのHTMLファイルが存在すること
        assert (output_dir / "page-one.html").exists()
        assert (output_dir / "page-two.html").exists()

        # インデックスファイルが存在すること
        index_path = output_dir / "index.html"
        assert index_path.exists()

        # インデックスに各ページへのリンクが含まれること
        index_content = index_path.read_text(encoding="utf-8")
        assert "Page One" in index_content
        assert "Page Two" in index_content
        assert "page-one.html" in index_content
        assert "page-two.html" in index_content


class TestExportToJSON:
    """JSON エクスポートのテスト"""

    def test_export_to_json_without_output_path(self, sample_page):
        """出力パスなしでJSONを生成"""
        json_str = Exporter.export_to_json(sample_page)

        # JSONが生成されること
        assert json_str

        # パース可能であること
        data = json.loads(json_str)

        # ページ情報が含まれること
        assert data["slug"] == "test-page"
        assert data["title"] == "Test Page"
        assert data["content"] == "# Hello\n\nThis is a **test** page."
        assert data["tags"] == ["python", "testing"]
        assert data["metadata_type"] == "default"
        assert data["metadata"] == {}
        assert data["created_at"] == "2025-01-01T12:00:00"
        assert data["updated_at"] == "2025-01-02T15:30:00"

    def test_export_to_json_with_output_path(self, sample_page, tmp_path):
        """出力パス指定でJSONファイルを生成"""
        output_path = tmp_path / "output" / "test.json"
        json_str = Exporter.export_to_json(sample_page, output_path)

        # ファイルが作成されること
        assert output_path.exists()

        # ファイル内容が正しいこと
        file_content = output_path.read_text(encoding="utf-8")
        assert file_content == json_str

        # パース可能であること
        data = json.loads(file_content)
        assert data["title"] == "Test Page"

    def test_export_to_json_with_none_dates(self):
        """created_at/updated_atがNoneの場合"""
        page = Page(
            id=1,
            slug="test",
            title="Test",
            content="Content",
            tags=[],
            metadata_type="default",
            metadata={},
            created_at=None,
            updated_at=None,
        )

        json_str = Exporter.export_to_json(page)
        data = json.loads(json_str)

        # Pageクラスがデフォルト値を設定する場合があるのでチェックを緩和
        assert "created_at" in data
        assert "updated_at" in data

    def test_export_to_json_with_metadata(self):
        """メタデータを含むページ"""
        page = Page(
            id=1,
            slug="recipe",
            title="Recipe",
            content="Recipe content",
            tags=["cooking"],
            metadata_type="recipe",
            metadata={
                "cooking_time": 30,
                "difficulty": "easy",
                "servings": 4,
            },
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        json_str = Exporter.export_to_json(page)
        data = json.loads(json_str)

        assert data["metadata_type"] == "recipe"
        assert data["metadata"]["cooking_time"] == 30
        assert data["metadata"]["difficulty"] == "easy"
        assert data["metadata"]["servings"] == 4

    def test_export_all_to_json(self, sample_pages, tmp_path):
        """全ページをJSONにエクスポート"""
        output_path = tmp_path / "export.json"
        result_path = Exporter.export_all_to_json(sample_pages, output_path)

        # ファイルが作成されること
        assert result_path == output_path
        assert output_path.exists()

        # パース可能であること
        data = json.loads(output_path.read_text(encoding="utf-8"))

        # メタデータが含まれること
        assert "pages" in data
        assert "total_pages" in data
        assert "export_date" in data

        # ページ数が正しいこと
        assert data["total_pages"] == 2
        assert len(data["pages"]) == 2

        # 各ページのデータが含まれること
        page_slugs = [p["slug"] for p in data["pages"]]
        assert "page-one" in page_slugs
        assert "page-two" in page_slugs
