"""プラグイン基底クラスのテスト"""

from typing import Any

from notenest.plugins.base import MetadataPlugin


class TestMetadataPlugin(MetadataPlugin):
    """テスト用メタデータプラグイン"""

    @property
    def name(self) -> str:
        return "test"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def metadata_type(self) -> str:
        return "test"

    def get_schema(self) -> dict[str, Any]:
        return {
            "required_field": {"type": "str", "required": True},
            "optional_field": {"type": "int", "required": False, "default": 42},
        }


def test_metadata_plugin_validation():
    """メタデータプラグインのバリデーションテスト"""
    plugin = TestMetadataPlugin()

    # 有効なデータ
    valid_data = {"required_field": "test", "optional_field": 100}
    is_valid, errors = plugin.validate(valid_data)
    assert is_valid
    assert len(errors) == 0

    # 必須フィールド不足
    invalid_data = {"optional_field": 100}
    is_valid, errors = plugin.validate(invalid_data)
    assert not is_valid
    assert len(errors) > 0

    # 型不一致
    invalid_type_data = {"required_field": "test", "optional_field": "not_an_int"}
    is_valid, errors = plugin.validate(invalid_type_data)
    assert not is_valid


def test_metadata_plugin_defaults():
    """デフォルト値取得のテスト"""
    plugin = TestMetadataPlugin()
    defaults = plugin.get_default_values()

    assert "optional_field" in defaults
    assert defaults["optional_field"] == 42
