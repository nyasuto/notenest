"""FastAPI application"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

# ルーター登録（APIルートは /api/ 配下のみ）
app.include_router(pages.router, prefix="/api/pages", tags=["pages"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["plugins"])


@app.get("/api")
async def api_root() -> dict[str, str]:
    """API ルートエンドポイント"""
    return {"message": "NoteNest API", "version": "0.1.0"}


@app.get("/api/health")
async def health() -> dict[str, str]:
    """ヘルスチェック"""
    return {"status": "ok"}


# 静的ファイル配信（本番モード用）
# フロントエンドのビルド済みファイルを配信
static_dir = Path(__file__).parent.parent / "frontend" / "dist"
if static_dir.exists():
    # 静的ファイル（JS, CSS、画像など）をマウント
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    # SPAのフォールバック: すべてのルートでindex.htmlを返す
    # 注意: これは最後に定義すること（APIルートより後）
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
