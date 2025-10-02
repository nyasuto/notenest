"""Recipe Plugin - レシピ管理用メタデータプラグイン"""

from typing import Any

from notenest.plugins.base import MetadataPlugin


class RecipePlugin(MetadataPlugin):
    """レシピ管理用のメタデータプラグイン

    料理のレシピ情報を管理するためのカスタムメタデータを提供します。
    材料、調理時間、難易度、栄養情報などを扱います。
    """

    @property
    def name(self) -> str:
        return "recipe"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "レシピ管理用のメタデータプラグイン"

    @property
    def metadata_type(self) -> str:
        return "recipe"

    def get_schema(self) -> dict[str, Any]:
        """レシピ用メタデータスキーマ定義

        Returns:
            dict: レシピのカスタムフィールド定義
        """
        return {
            "ingredients": {
                "type": "list",
                "required": True,
                "default": [],
                "description": "材料リスト（各材料は文字列）",
            },
            "cooking_time": {
                "type": "int",
                "required": True,
                "default": 30,
                "description": "調理時間（分）",
            },
            "difficulty": {
                "type": "str",
                "required": True,
                "default": "medium",
                "description": "難易度（easy, medium, hard）",
            },
            "servings": {
                "type": "int",
                "required": True,
                "default": 2,
                "description": "何人分か",
            },
            "nutrition": {
                "type": "dict",
                "required": False,
                "default": {},
                "description": "栄養情報（calories, protein, carbs, fat など）",
            },
            "rating": {
                "type": "float",
                "required": False,
                "default": None,
                "description": "評価（0.0～5.0）",
            },
        }

    def validate(self, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """レシピデータのバリデーション

        基本的なバリデーションに加えて、レシピ固有のルールをチェックします。

        Args:
            data: バリデーション対象のデータ

        Returns:
            tuple: (is_valid, error_messages)
        """
        # 基本バリデーション
        is_valid, errors = super().validate(data)

        # 難易度の値チェック
        if "difficulty" in data:
            difficulty = data["difficulty"]
            valid_difficulties = ["easy", "medium", "hard"]
            if difficulty not in valid_difficulties:
                errors.append(
                    f"difficulty must be one of {valid_difficulties}, got '{difficulty}'"
                )

        # 調理時間の範囲チェック
        if "cooking_time" in data:
            cooking_time = data["cooking_time"]
            if isinstance(cooking_time, int) and cooking_time <= 0:
                errors.append("cooking_time must be greater than 0")

        # 人数分の範囲チェック
        if "servings" in data:
            servings = data["servings"]
            if isinstance(servings, int) and servings <= 0:
                errors.append("servings must be greater than 0")

        # 評価の範囲チェック
        if "rating" in data and data["rating"] is not None:
            rating = data["rating"]
            if isinstance(rating, (int, float)) and (rating < 0.0 or rating > 5.0):
                errors.append("rating must be between 0.0 and 5.0")

        return len(errors) == 0, errors

    def on_page_create(self, page_id: int, data: dict[str, Any]) -> None:
        """ページ作成時のフック

        レシピページが作成されたときに呼び出されます。

        Args:
            page_id: 作成されたページのID
            data: ページのメタデータ
        """
        # 将来的には、レシピカタログへの自動登録などを実装可能
        pass

    def on_page_update(self, page_id: int, data: dict[str, Any]) -> None:
        """ページ更新時のフック

        レシピページが更新されたときに呼び出されます。

        Args:
            page_id: 更新されたページのID
            data: 更新後のメタデータ
        """
        # 将来的には、更新履歴の記録などを実装可能
        pass

    def on_page_delete(self, page_id: int) -> None:
        """ページ削除時のフック

        レシピページが削除されたときに呼び出されます。

        Args:
            page_id: 削除されたページのID
        """
        # 将来的には、カタログからの削除などを実装可能
        pass
