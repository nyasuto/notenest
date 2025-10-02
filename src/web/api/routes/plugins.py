"""Plugins API routes"""

from fastapi import APIRouter

from notenest.plugins.base import MetadataPlugin
from notenest.plugins.registry import PluginRegistry
from web.api.main import get_plugin_registry
from web.api.models import PluginResponse

router = APIRouter()


@router.get("", response_model=list[PluginResponse])
async def list_plugins() -> list[PluginResponse]:
    """プラグイン一覧を取得"""
    registry: PluginRegistry = get_plugin_registry()
    plugins = registry.list_plugins()

    plugin_responses = []
    for plugin in plugins:
        metadata_type = None
        if isinstance(plugin, MetadataPlugin):
            metadata_type = plugin.metadata_type

        plugin_responses.append(
            PluginResponse(
                name=plugin.name,
                version=plugin.version,
                description=plugin.description,
                metadata_type=metadata_type,
            )
        )

    return plugin_responses


@router.get("/metadata/{metadata_type}/schema")
async def get_plugin_schema(metadata_type: str) -> dict[str, object]:
    """プラグインのスキーマを取得"""
    registry: PluginRegistry = get_plugin_registry()
    plugin = registry.get_metadata_plugin(metadata_type)

    if not plugin:
        return {}

    return plugin.get_schema()
