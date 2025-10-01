"""DBStoreのテスト"""

import tempfile
from pathlib import Path

from notenest.core.page import Page
from notenest.storage.db_store import DBStore


def test_foreign_key_cascade_on_delete():
    """外部キー制約によるカスケード削除のテスト"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmpfile:
        db_path = Path(tmpfile.name)

    try:
        db = DBStore(db_path)
        db.connect()

        # ページ作成
        page = Page(slug="test-page", title="Test Page")
        page_id = db.save_page(page)

        # タグ追加
        db.save_page_tags(page_id, ["tag1", "tag2"])

        # リンク追加
        db.save_links(page_id, ["target1", "target2"])

        # 削除前の確認
        assert len(db.get_page_tags(page_id)) == 2
        assert len(db.get_outgoing_links(page_id)) == 2

        # ページ削除
        db.delete_page(page_id)

        # カスケード削除の確認
        # タグ関連が削除されているか
        assert len(db.get_page_tags(page_id)) == 0

        # リンクが削除されているか
        assert len(db.get_outgoing_links(page_id)) == 0

        db.close()
    finally:
        db_path.unlink(missing_ok=True)
