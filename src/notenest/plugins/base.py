"""プラグイン基底クラス"""

from abc import ABC, abstractmethod
from typing import Any


class BasePlugin(ABC):
    """全プラグインの基底クラス"""

    @property
    @abstractmethod
    def name(self) -> str:
        """プラグイン名"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """プラグインバージョン"""
        pass

    @property
    def description(self) -> str:
        """プラグインの説明"""
        return ""

    def on_load(self) -> None:
        """プラグイン読み込み時のフック"""
        pass

    def on_unload(self) -> None:
        """プラグインアンロード時のフック"""
        pass


class MetadataPlugin(BasePlugin):
    """メタデータ拡張プラグインの基底クラス"""

    @property
    @abstractmethod
    def metadata_type(self) -> str:
        """メタデータ型名（ページのmetadata_typeとして使用）"""
        pass

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """
        カスタムフィールドのスキーマ定義

        Returns:
            dict: フィールド名をキー、スキーマ定義を値とする辞書

        Example:
            {
                "field_name": {
                    "type": "str",  # str, int, float, bool, list, dict
                    "required": True,
                    "default": None,
                    "description": "Field description"
                }
            }
        """
        pass

    def validate(self, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        データのバリデーション

        Args:
            data: バリデーション対象のデータ

        Returns:
            tuple: (is_valid, error_messages)
        """
        schema = self.get_schema()
        errors: list[str] = []

        # 必須フィールドチェック
        for field_name, field_schema in schema.items():
            if field_schema.get("required", False) and (
                field_name not in data or data[field_name] is None
            ):
                errors.append(f"Required field '{field_name}' is missing")

        # 型チェック
        for field_name, value in data.items():
            if field_name not in schema:
                continue

            field_schema = schema[field_name]
            expected_type = field_schema.get("type")

            if expected_type and value is not None:
                type_map = {
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                }

                if expected_type in type_map and not isinstance(value, type_map[expected_type]):
                    errors.append(
                        f"Field '{field_name}' should be {expected_type}, got {type(value).__name__}"
                    )

        return len(errors) == 0, errors

    def get_default_values(self) -> dict[str, Any]:
        """デフォルト値を取得"""
        schema = self.get_schema()
        defaults = {}

        for field_name, field_schema in schema.items():
            if "default" in field_schema:
                defaults[field_name] = field_schema["default"]

        return defaults

    def on_page_create(self, page_id: int, data: dict[str, Any]) -> None:
        """ページ作成時のフック"""
        pass

    def on_page_update(self, page_id: int, data: dict[str, Any]) -> None:
        """ページ更新時のフック"""
        pass

    def on_page_delete(self, page_id: int) -> None:
        """ページ削除時のフック"""
        pass


class ExternalDataPlugin(BasePlugin):
    """外部データベース連携プラグインの基底クラス"""

    @abstractmethod
    async def fetch_data(self, query: str) -> list[dict[str, Any]]:
        """
        外部DBからデータ取得

        Args:
            query: クエリ文字列

        Returns:
            list: 取得したデータのリスト
        """
        pass

    @abstractmethod
    async def sync_to_external(self, page_id: int, data: dict[str, Any]) -> bool:
        """
        外部DBへの同期

        Args:
            page_id: ページID
            data: 同期するデータ

        Returns:
            bool: 成功したかどうか
        """
        pass

    async def sync_from_external(self, external_id: str) -> dict[str, Any] | None:
        """
        外部DBから単一データを取得

        Args:
            external_id: 外部データのID

        Returns:
            dict | None: 取得したデータ、存在しない場合はNone
        """
        return None
