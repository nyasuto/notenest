"""リンクモデル"""

from dataclasses import dataclass


@dataclass
class Link:
    """ページ間のリンクを表すモデル"""

    id: int | None = None
    source_page_id: int | None = None  # リンク元ページID
    source_slug: str = ""  # リンク元ページslug
    target_slug: str = ""  # リンク先ページslug（未作成ページも許可）
    link_type: str = "wiki"  # wiki, external など

    @property
    def is_broken(self) -> bool:
        """リンク切れかどうか（未作成ページへのリンク）"""
        # 実際の判定はストレージ層で行う
        return False
