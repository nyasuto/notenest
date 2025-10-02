"""プラグインレジストリのテスト"""

import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

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


class AnotherDummyPlugin(MetadataPlugin):
    """テスト用ダミープラグイン2（metadata_typeが同じ）"""

    @property
    def name(self) -> str:
        return "another_dummy"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def metadata_type(self) -> str:
        return "dummy"  # 同じmetadata_type

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


def test_plugin_registry_duplicate_metadata_type():
    """metadata_typeが重複する場合にエラーが発生することを確認"""
    registry = PluginRegistry()

    # 最初のプラグインを登録
    plugin1 = DummyPlugin()
    registry.register(plugin1)

    # 同じmetadata_typeを持つプラグインを登録しようとするとエラー
    plugin2 = AnotherDummyPlugin()
    with pytest.raises(ValueError, match="Metadata type 'dummy' is already registered"):
        registry.register(plugin2)

    # 最初のプラグインのみが登録されている
    assert len(registry.list_plugins()) == 1
    assert registry.get_plugin("dummy") == plugin1
    assert registry.get_plugin("another_dummy") is None


def test_plugin_registry_discover_external_directory():
    """sys.path外のディレクトリからプラグインを検出できることを確認"""
    registry = PluginRegistry()

    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        plugin_dir = tmpdir_path / "test_plugins"
        plugin_dir.mkdir()

        # プラグインファイルを作成
        plugin_file = plugin_dir / "external_plugin.py"
        plugin_code = """
from typing import Any
from notenest.plugins.base import MetadataPlugin

class ExternalPlugin(MetadataPlugin):
    @property
    def name(self) -> str:
        return "external"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def metadata_type(self) -> str:
        return "external"

    def get_schema(self) -> dict[str, Any]:
        return {}
"""
        plugin_file.write_text(plugin_code)

        # sys.pathに含まれていないことを確認
        assert str(tmpdir_path) not in sys.path

        # プラグインを検出
        registered = registry.discover_plugins(plugin_dir)

        # プラグインが登録されたことを確認
        assert len(registered) == 1
        assert "external" in registered
        assert registry.get_metadata_plugin("external") is not None

        # sys.pathから削除されたことを確認（クリーンアップ）
        assert str(tmpdir_path) not in sys.path
