"""FastAPI application"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from notenest.core.repository import Repository
from notenest.plugins.registry import PluginRegistry, get_global_registry
from web.api.routes import pages, plugins, search, tags

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


# FastAPIアプリケーション作成
app = FastAPI(
    title="NoteNest API",
    description="マークダウンベース ナレッジベース・Wikiシステム",
    version="0.1.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite/React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(pages.router, prefix="/api/pages", tags=["pages"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["plugins"])


@app.get("/")
async def root() -> dict[str, str]:
    """ルートエンドポイント"""
    return {"message": "NoteNest API", "version": "0.1.0"}


@app.get("/api/health")
async def health() -> dict[str, str]:
    """ヘルスチェック"""
    return {"status": "ok"}
