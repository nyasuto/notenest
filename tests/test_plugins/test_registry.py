"""プラグインレジストリのテスト"""

from typing import Any

from notenest.plugins.base import MetadataPlugin
from notenest.plugins.registry import PluginRegistry


class DummyPlugin(MetadataPlugin):
    """テスト用ダミープラグイン"""

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def metadata_type(self) -> str:
        return "dummy"

    def get_schema(self) -> dict[str, Any]:
        return {}


def test_plugin_registry_register():
    """プラグイン登録のテスト"""
    registry = PluginRegistry()
    plugin = DummyPlugin()

    registry.register(plugin)

    assert len(registry.list_plugins()) == 1
    assert registry.get_plugin("dummy") == plugin
    assert registry.get_metadata_plugin("dummy") == plugin


def test_plugin_registry_unregister():
    """プラグイン登録解除のテスト"""
    registry = PluginRegistry()
    plugin = DummyPlugin()

    registry.register(plugin)
    assert len(registry.list_plugins()) == 1

    registry.unregister("dummy")
    assert len(registry.list_plugins()) == 0
    assert registry.get_plugin("dummy") is None


def test_plugin_registry_list():
    """プラグインリスト取得のテスト"""
    registry = PluginRegistry()

    plugin1 = DummyPlugin()
    registry.register(plugin1)

    assert len(registry.list_plugins()) == 1
    assert len(registry.list_metadata_plugins()) == 1
