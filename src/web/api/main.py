"""FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web.api.routes import pages, plugins, search, tags

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
