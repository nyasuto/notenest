"""デフォルトメタデータプラグイン"""

from typing import Any

from notenest.plugins.base import MetadataPlugin


class DefaultPlugin(MetadataPlugin):
    """デフォルトのメタデータプラグイン（基本的なページ情報のみ）"""

    @property
    def name(self) -> str:
        return "default"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "デフォルトのメタデータプラグイン（基本ページ情報）"

    @property
    def metadata_type(self) -> str:
        return "default"

    def get_schema(self) -> dict[str, Any]:
        """
        デフォルトプラグインはカスタムフィールドを持たない
        title, tags などは core で管理
        """
        return {}
