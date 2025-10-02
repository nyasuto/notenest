"""API dependencies"""

from pathlib import Path

from notenest.core.repository import Repository
from notenest.plugins.registry import PluginRegistry, get_global_registry

# グローバル状態
app_state: dict[str, object] = {}


def get_repository() -> Repository:
    """Repositoryインスタンスを取得"""
    if "repository" not in app_state:
        workspace = Path("./workspace")
        workspace.mkdir(exist_ok=True)
        app_state["repository"] = Repository(workspace)
    return app_state["repository"]  # type: ignore


def get_plugin_registry() -> PluginRegistry:
    """PluginRegistryインスタンスを取得"""
    return get_global_registry()
