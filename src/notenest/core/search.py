"""高度な検索機能"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from notenest.core.page import Page


class SearchOperator(Enum):
    """検索演算子"""

    AND = "AND"
    OR = "OR"


class SearchField(Enum):
    """検索対象フィールド"""

    TITLE = "title"
    CONTENT = "content"
    TAGS = "tags"
    METADATA = "metadata"
    ALL = "all"


@dataclass
class SearchCondition:
    """検索条件"""

    field: SearchField
    value: Any
    operator: SearchOperator = SearchOperator.AND


@dataclass
class DateRangeFilter:
    """日付範囲フィルタ"""

    start_date: datetime | None = None
    end_date: datetime | None = None


class AdvancedSearch:
    """高度な検索機能"""

    @staticmethod
    def filter_by_date_range(
        pages: list[Page], date_range: DateRangeFilter, date_field: str = "updated_at"
    ) -> list[Page]:
        """
        日付範囲でフィルタリング

        Args:
            pages: ページリスト
            date_range: 日付範囲フィルタ
            date_field: 対象の日付フィールド（created_at or updated_at）

        Returns:
            list: フィルタリングされたページリスト
        """
        filtered = []

        for page in pages:
            page_date = getattr(page, date_field, None)
            if page_date is None:
                continue

            # 開始日チェック
            if date_range.start_date and page_date < date_range.start_date:
                continue

            # 終了日チェック
            if date_range.end_date and page_date > date_range.end_date:
                continue

            filtered.append(page)

        return filtered

    @staticmethod
    def filter_by_metadata_field(
        pages: list[Page], field_name: str, field_value: Any
    ) -> list[Page]:
        """
        メタデータフィールドでフィルタリング

        Args:
            pages: ページリスト
            field_name: メタデータフィールド名
            field_value: フィールド値（部分一致）

        Returns:
            list: フィルタリングされたページリスト
        """
        filtered = []

        for page in pages:
            if field_name not in page.metadata:
                continue

            page_value = page.metadata[field_name]

            # 値の比較
            if isinstance(field_value, str) and isinstance(page_value, str):
                # 文字列の部分一致
                if field_value.lower() in page_value.lower():
                    filtered.append(page)
            elif isinstance(field_value, (int, float)):
                # 数値の完全一致
                if page_value == field_value:
                    filtered.append(page)
            elif isinstance(field_value, list):
                # リストの包含チェック
                if isinstance(page_value, list) and any(item in page_value for item in field_value):
                    filtered.append(page)
            else:
                # その他は完全一致
                if page_value == field_value:
                    filtered.append(page)

        return filtered

    @staticmethod
    def filter_by_metadata_type(pages: list[Page], metadata_type: str) -> list[Page]:
        """メタデータ型でフィルタリング"""
        return [page for page in pages if page.metadata_type == metadata_type]

    @staticmethod
    def filter_by_tags(pages: list[Page], tags: list[str], match_all: bool = False) -> list[Page]:
        """
        タグでフィルタリング

        Args:
            pages: ページリスト
            tags: タグリスト
            match_all: True=全タグに一致, False=いずれかのタグに一致

        Returns:
            list: フィルタリングされたページリスト
        """
        filtered = []

        for page in pages:
            if match_all:
                # 全タグに一致
                if all(tag in page.tags for tag in tags):
                    filtered.append(page)
            else:
                # いずれかのタグに一致
                if any(tag in page.tags for tag in tags):
                    filtered.append(page)

        return filtered

    @staticmethod
    def sort_pages(
        pages: list[Page], sort_by: str = "updated_at", reverse: bool = True
    ) -> list[Page]:
        """
        ページをソート

        Args:
            pages: ページリスト
            sort_by: ソートキー（created_at, updated_at, title, slug）
            reverse: True=降順, False=昇順

        Returns:
            list: ソート済みページリスト
        """
        if sort_by == "title":
            return sorted(pages, key=lambda p: p.title.lower(), reverse=reverse)
        elif sort_by == "slug":
            return sorted(pages, key=lambda p: p.slug.lower(), reverse=reverse)
        elif sort_by == "created_at":
            return sorted(
                pages,
                key=lambda p: p.created_at or datetime.min,
                reverse=reverse,
            )
        elif sort_by == "updated_at":
            return sorted(
                pages,
                key=lambda p: p.updated_at or datetime.min,
                reverse=reverse,
            )
        else:
            return pages

    @classmethod
    def complex_search(
        cls,
        pages: list[Page],
        text_query: str | None = None,
        tags: list[str] | None = None,
        metadata_type: str | None = None,
        metadata_filters: dict[str, Any] | None = None,
        date_range: DateRangeFilter | None = None,
        sort_by: str = "updated_at",
        reverse: bool = True,
    ) -> list[Page]:
        """
        複合検索

        Args:
            pages: ページリスト
            text_query: テキスト検索クエリ（タイトル・コンテンツに対して）
            tags: タグリスト
            metadata_type: メタデータ型
            metadata_filters: メタデータフィールドフィルタ
            date_range: 日付範囲フィルタ
            sort_by: ソートキー
            reverse: ソート順

        Returns:
            list: 検索結果
        """
        result = pages

        # テキスト検索
        if text_query:
            result = [
                p
                for p in result
                if text_query.lower() in p.title.lower() or text_query.lower() in p.content.lower()
            ]

        # タグフィルタ
        if tags:
            result = cls.filter_by_tags(result, tags, match_all=False)

        # メタデータ型フィルタ
        if metadata_type:
            result = cls.filter_by_metadata_type(result, metadata_type)

        # メタデータフィールドフィルタ
        if metadata_filters:
            for field_name, field_value in metadata_filters.items():
                result = cls.filter_by_metadata_field(result, field_name, field_value)

        # 日付範囲フィルタ
        if date_range:
            result = cls.filter_by_date_range(result, date_range)

        # ソート
        result = cls.sort_pages(result, sort_by, reverse)

        return result
