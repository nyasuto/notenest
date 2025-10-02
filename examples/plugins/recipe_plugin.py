"""レシピプラグインのサンプル実装"""

from typing import Any

from notenest.plugins.base import MetadataPlugin


class RecipePlugin(MetadataPlugin):
    """料理レシピ用メタデータプラグイン"""

    @property
    def name(self) -> str:
        return "recipe"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "料理レシピ管理用のメタデータプラグイン"

    @property
    def metadata_type(self) -> str:
        return "recipe"

    def get_schema(self) -> dict[str, Any]:
        """レシピ用カスタムフィールドのスキーマ定義"""
        return {
            "ingredients": {
                "type": "list",
                "required": True,
                "description": "材料リスト（例: ['卵 2個', '砂糖 50g']）",
            },
            "cooking_time": {
                "type": "int",
                "required": True,
                "description": "調理時間（分）",
            },
            "difficulty": {
                "type": "str",
                "required": False,
                "default": "medium",
                "enum": ["easy", "medium", "hard"],
                "description": "難易度",
            },
            "servings": {
                "type": "int",
                "required": False,
                "default": 2,
                "description": "何人分",
            },
            "nutrition": {
                "type": "dict",
                "required": False,
                "description": "栄養情報（例: {'calories': 300, 'protein': 20}）",
            },
            "rating": {
                "type": "float",
                "required": False,
                "description": "評価（0.0-5.0）",
            },
            "notes": {
                "type": "str",
                "required": False,
                "description": "メモ・コツ",
            },
        }

    def validate(self, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """レシピデータのバリデーション"""
        is_valid, errors = super().validate(data)

        # カスタムバリデーション
        if "rating" in data and data["rating"] is not None:
            rating = data["rating"]
            if not (0.0 <= rating <= 5.0):
                errors.append("Rating must be between 0.0 and 5.0")
                is_valid = False

        if "difficulty" in data and data["difficulty"] is not None:
            if data["difficulty"] not in ["easy", "medium", "hard"]:
                errors.append("Difficulty must be 'easy', 'medium', or 'hard'")
                is_valid = False

        if "cooking_time" in data and data["cooking_time"] is not None:
            if data["cooking_time"] <= 0:
                errors.append("Cooking time must be positive")
                is_valid = False

        return is_valid, errors

    def on_page_create(self, page_id: int, data: dict[str, Any]) -> None:
        """レシピページ作成時の処理"""
        print(f"Recipe created: page_id={page_id}, ingredients={data.get('ingredients', [])}")

    def on_page_update(self, page_id: int, data: dict[str, Any]) -> None:
        """レシピページ更新時の処理"""
        print(f"Recipe updated: page_id={page_id}")

    def on_page_delete(self, page_id: int) -> None:
        """レシピページ削除時の処理"""
        print(f"Recipe deleted: page_id={page_id}")
