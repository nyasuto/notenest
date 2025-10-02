"""プラグイン登録・管理"""

import importlib
import inspect
import sys
from pathlib import Path

from notenest.plugins.base import BasePlugin, ExternalDataPlugin, MetadataPlugin


class PluginRegistry:
    """プラグイン登録・管理クラス"""

    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}
        self._metadata_plugins: dict[str, MetadataPlugin] = {}
        self._external_plugins: dict[str, ExternalDataPlugin] = {}

    def register(self, plugin: BasePlugin) -> None:
        """
        プラグインを登録

        Args:
            plugin: 登録するプラグインインスタンス
        """
        plugin_name = plugin.name

        if plugin_name in self._plugins:
            raise ValueError(f"Plugin '{plugin_name}' is already registered")

        # 型別の重複チェック
        if isinstance(plugin, MetadataPlugin) and plugin.metadata_type in self._metadata_plugins:
            raise ValueError(
                f"Metadata type '{plugin.metadata_type}' is already registered "
                f"by plugin '{self._metadata_plugins[plugin.metadata_type].name}'"
            )

        self._plugins[plugin_name] = plugin

        # 型別に分類
        if isinstance(plugin, MetadataPlugin):
            self._metadata_plugins[plugin.metadata_type] = plugin

        if isinstance(plugin, ExternalDataPlugin):
            self._external_plugins[plugin_name] = plugin

        # プラグイン読み込みフック
        plugin.on_load()

    def unregister(self, plugin_name: str) -> None:
        """
        プラグインを登録解除

        Args:
            plugin_name: プラグイン名
        """
        if plugin_name not in self._plugins:
            return

        plugin = self._plugins[plugin_name]

        # アンロードフック
        plugin.on_unload()

        # 登録解除
        del self._plugins[plugin_name]

        if isinstance(plugin, MetadataPlugin) and plugin.metadata_type in self._metadata_plugins:
            del self._metadata_plugins[plugin.metadata_type]

        if isinstance(plugin, ExternalDataPlugin) and plugin_name in self._external_plugins:
            del self._external_plugins[plugin_name]

    def get_plugin(self, plugin_name: str) -> BasePlugin | None:
        """プラグインを取得"""
        return self._plugins.get(plugin_name)

    def get_metadata_plugin(self, metadata_type: str) -> MetadataPlugin | None:
        """メタデータプラグインを型名で取得"""
        return self._metadata_plugins.get(metadata_type)

    def get_external_plugin(self, plugin_name: str) -> ExternalDataPlugin | None:
        """外部データプラグインを取得"""
        return self._external_plugins.get(plugin_name)

    def list_plugins(self) -> list[BasePlugin]:
        """全プラグインをリスト"""
        return list(self._plugins.values())

    def list_metadata_plugins(self) -> list[MetadataPlugin]:
        """全メタデータプラグインをリスト"""
        return list(self._metadata_plugins.values())

    def list_external_plugins(self) -> list[ExternalDataPlugin]:
        """全外部データプラグインをリスト"""
        return list(self._external_plugins.values())

    def discover_plugins(self, plugin_dir: Path) -> list[str]:
        """
        指定ディレクトリからプラグインを自動検出・登録

        Args:
            plugin_dir: プラグインディレクトリ

        Returns:
            list: 登録されたプラグイン名のリスト
        """
        if not plugin_dir.exists() or not plugin_dir.is_dir():
            return []

        registered_plugins: list[str] = []

        # plugin_dir.parentをsys.pathに一時的に追加
        plugin_parent = str(plugin_dir.parent.resolve())
        path_added = plugin_parent not in sys.path

        if path_added:
            sys.path.insert(0, plugin_parent)

        try:
            # Pythonファイルを検索
            for py_file in plugin_dir.glob("**/*.py"):
                if py_file.name.startswith("_"):
                    continue

                try:
                    # モジュールパス構築
                    relative_path = py_file.relative_to(plugin_dir.parent)
                    module_path = str(relative_path.with_suffix("")).replace("/", ".")

                    # モジュールインポート
                    module = importlib.import_module(module_path)

                    # プラグインクラスを探す
                    for _name, obj in inspect.getmembers(module, inspect.isclass):
                        # BasePluginのサブクラスで、BasePlugin自体でない
                        if (
                            issubclass(obj, BasePlugin)
                            and obj not in (BasePlugin, MetadataPlugin, ExternalDataPlugin)
                            and not inspect.isabstract(obj)
                        ):
                            # インスタンス化して登録
                            plugin_instance = obj()
                            self.register(plugin_instance)
                            registered_plugins.append(plugin_instance.name)

                except Exception as e:
                    # エラーは無視（ロギング推奨）
                    print(f"Failed to load plugin from {py_file}: {e}")
                    continue
        finally:
            # sys.pathから削除（追加した場合のみ）
            if path_added and plugin_parent in sys.path:
                sys.path.remove(plugin_parent)

        return registered_plugins

    def load_plugin_from_module(self, module_path: str, class_name: str) -> bool:
        """
        モジュールパスとクラス名からプラグインを読み込み

        Args:
            module_path: モジュールパス（例: "notenest.plugins.builtin.default"）
            class_name: クラス名（例: "DefaultPlugin"）

        Returns:
            bool: 成功したかどうか
        """
        try:
            module = importlib.import_module(module_path)
            plugin_class: type[BasePlugin] = getattr(module, class_name)

            if not issubclass(plugin_class, BasePlugin):
                return False

            plugin_instance = plugin_class()
            self.register(plugin_instance)
            return True

        except Exception as e:
            print(f"Failed to load plugin {class_name} from {module_path}: {e}")
            return False


# グローバルレジストリインスタンス
_global_registry: PluginRegistry | None = None


def get_global_registry() -> PluginRegistry:
    """グローバルプラグインレジストリを取得"""
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
    return _global_registry
