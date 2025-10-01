"""タグモデル"""

from dataclasses import dataclass


@dataclass
class Tag:
    """タグを表すモデル"""

    id: int | None = None
    name: str = ""
    page_count: int = 0  # このタグが付けられているページ数

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return False
        return self.name == other.name
