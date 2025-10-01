"""Textual TUIメインアプリケーション"""

import os
import subprocess
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, Markdown, Static

from notenest.core.repository import Repository


class PageListItem(ListItem):
    """ページリストアイテム"""

    def __init__(self, slug: str, title: str, tags: list[str]) -> None:
        super().__init__()
        self.slug = slug
        self.title = title
        self.tags = tags

    def compose(self) -> ComposeResult:
        tags_str = f"[{', '.join(self.tags)}]" if self.tags else ""
        yield Label(f"{self.title} {tags_str}")


class NoteNestApp(App[None]):
    """NoteNest TUIアプリケーション"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 3;
        grid-columns: 1fr 2fr 2fr;
    }

    #sidebar {
        column-span: 1;
        border: solid green;
    }

    #preview {
        column-span: 2;
        border: solid blue;
        overflow-y: auto;
    }

    #search-box {
        dock: top;
        height: 3;
    }

    #page-list {
        height: 100%;
    }

    #info-panel {
        dock: bottom;
        height: 5;
        border: solid yellow;
    }
    """

    BINDINGS = [
        Binding("ctrl+c,q", "quit", "Quit"),
        Binding("n", "new_page", "New Page"),
        Binding("e", "edit_page", "Edit"),
        Binding("d", "delete_page", "Delete"),
        Binding("s", "search", "Search"),
        Binding("t", "show_tags", "Tags"),
        Binding("b", "show_backlinks", "Backlinks"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, workspace_path: Path) -> None:
        super().__init__()
        self.workspace_path = workspace_path
        self.repo = Repository(workspace_path)
        self.current_page_slug: str | None = None

    def compose(self) -> ComposeResult:
        """UIコンポーネント構成"""
        yield Header()

        # サイドバー（ページリスト）
        with Vertical(id="sidebar"):
            yield Input(placeholder="Search...", id="search-box")
            yield ListView(id="page-list")

        # プレビューエリア
        with Vertical(id="preview"):
            yield Markdown("# Welcome to NoteNest\n\nSelect a page from the list or create a new one (n).")
            yield Static("", id="info-panel")

        yield Footer()

    def on_mount(self) -> None:
        """マウント時の処理"""
        # ファイルシステムから同期
        self.repo.sync_from_files()
        self.refresh_page_list()

    def refresh_page_list(self) -> None:
        """ページリストを更新"""
        page_list = self.query_one("#page-list", ListView)
        page_list.clear()

        pages = self.repo.list_pages()
        for page in pages:
            item = PageListItem(page.slug, page.title, page.tags)
            page_list.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """ページリスト選択時"""
        if isinstance(event.item, PageListItem):
            self.show_page(event.item.slug)

    def show_page(self, slug: str) -> None:
        """ページを表示"""
        page = self.repo.get_page(slug)
        if not page:
            return

        self.current_page_slug = slug

        # プレビュー更新
        preview = self.query_one("#preview Markdown")
        preview.update(f"# {page.title}\n\n{page.content}")

        # 情報パネル更新
        info_panel = self.query_one("#info-panel", Static)
        tags_str = ", ".join(page.tags) if page.tags else "None"
        backlinks = self.repo.get_backlinks(slug)
        backlinks_count = len(backlinks)

        info_text = f"Slug: {page.slug} | Tags: {tags_str} | Backlinks: {backlinks_count}"
        if page.created_at:
            info_text += f" | Created: {page.created_at.strftime('%Y-%m-%d')}"
        if page.updated_at:
            info_text += f" | Updated: {page.updated_at.strftime('%Y-%m-%d')}"

        info_panel.update(info_text)

    def action_new_page(self) -> None:
        """新規ページ作成"""
        # 簡易実装: slugとtitleを入力させる
        self.push_screen("new_page_screen")

    def action_edit_page(self) -> None:
        """ページ編集（外部エディタ起動）"""
        if not self.current_page_slug:
            return

        page = self.repo.get_page(self.current_page_slug)
        if not page or not page.file_path:
            return

        # $EDITOR を使用して編集
        editor = os.environ.get("EDITOR", "vim")
        subprocess.run([editor, str(page.file_path)])

        # 編集後に再読み込み
        self.repo.sync_from_files()
        self.show_page(self.current_page_slug)
        self.refresh_page_list()

    def action_delete_page(self) -> None:
        """ページ削除"""
        if not self.current_page_slug:
            return

        # 確認なしで削除（本来は確認ダイアログを出すべき）
        self.repo.delete_page(self.current_page_slug)
        self.current_page_slug = None
        self.refresh_page_list()

        # プレビュークリア
        preview = self.query_one("#preview Markdown")
        preview.update("# Page Deleted\n\nSelect another page or create a new one.")

    def action_search(self) -> None:
        """検索にフォーカス"""
        search_box = self.query_one("#search-box", Input)
        search_box.focus()

    def action_show_tags(self) -> None:
        """タグ一覧表示"""
        tags = self.repo.get_all_tags()
        tags_md = "# Tags\n\n"
        for tag in tags:
            tags_md += f"- **{tag.name}** ({tag.page_count} pages)\n"

        preview = self.query_one("#preview Markdown")
        preview.update(tags_md)

    def action_show_backlinks(self) -> None:
        """バックリンク表示"""
        if not self.current_page_slug:
            return

        backlinks = self.repo.get_backlinks(self.current_page_slug)
        backlinks_md = f"# Backlinks to {self.current_page_slug}\n\n"

        if not backlinks:
            backlinks_md += "No backlinks found."
        else:
            for link in backlinks:
                backlinks_md += f"- [[{link.source_slug}]]\n"

        preview = self.query_one("#preview Markdown")
        preview.update(backlinks_md)

    def action_refresh(self) -> None:
        """リフレッシュ"""
        self.repo.sync_from_files()
        self.refresh_page_list()

    def on_input_changed(self, event: Input.Changed) -> None:
        """検索ボックス入力時"""
        if event.input.id == "search-box":
            query = event.value.strip()
            if not query:
                self.refresh_page_list()
                return

            # 検索実行
            results = self.repo.search_pages(query)

            # リスト更新
            page_list = self.query_one("#page-list", ListView)
            page_list.clear()

            for page in results:
                item = PageListItem(page.slug, page.title, page.tags)
                page_list.append(item)

    def on_unmount(self) -> None:
        """アンマウント時のクリーンアップ"""
        self.repo.close()
