"""Recipe Plugin のテスト"""

import sys
from pathlib import Path

import pytest

# examples/plugins をパスに追加
examples_path = Path(__file__).parent.parent.parent / "examples"
sys.path.insert(0, str(examples_path))

from plugins.recipe_plugin import RecipePlugin  # noqa: E402


class TestRecipePlugin:
    """RecipePluginのテストクラス"""

    @pytest.fixture
    def plugin(self):
        """RecipePluginインスタンスを返すフィクスチャ"""
        return RecipePlugin()

    def test_plugin_properties(self, plugin):
        """プラグインの基本プロパティテスト"""
        assert plugin.name == "recipe"
        assert plugin.version == "1.0.0"
        assert plugin.description == "レシピ管理用のメタデータプラグイン"
        assert plugin.metadata_type == "recipe"

    def test_schema(self, plugin):
        """スキーマ定義のテスト"""
        schema = plugin.get_schema()

        # 必須フィールドの確認
        assert "ingredients" in schema
        assert schema["ingredients"]["type"] == "list"
        assert schema["ingredients"]["required"] is True

        assert "cooking_time" in schema
        assert schema["cooking_time"]["type"] == "int"

        assert "difficulty" in schema
        assert schema["difficulty"]["type"] == "str"

        assert "servings" in schema
        assert schema["servings"]["type"] == "int"

        # オプショナルフィールドの確認
        assert "nutrition" in schema
        assert schema["nutrition"]["required"] is False

        assert "rating" in schema
        assert schema["rating"]["required"] is False

    def test_default_values(self, plugin):
        """デフォルト値のテスト"""
        defaults = plugin.get_default_values()

        assert defaults["ingredients"] == []
        assert defaults["cooking_time"] == 30
        assert defaults["difficulty"] == "medium"
        assert defaults["servings"] == 2
        assert defaults["nutrition"] == {}
        assert defaults["rating"] is None

    def test_validate_valid_data(self, plugin):
        """有効なデータのバリデーションテスト"""
        valid_data = {
            "ingredients": ["材料1", "材料2"],
            "cooking_time": 30,
            "difficulty": "medium",
            "servings": 2,
            "nutrition": {"calories": 500},
            "rating": 4.5,
        }

        is_valid, errors = plugin.validate(valid_data)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_minimal_data(self, plugin):
        """最小限のデータのバリデーションテスト"""
        minimal_data = {
            "ingredients": [],
            "cooking_time": 15,
            "difficulty": "easy",
            "servings": 1,
        }

        is_valid, errors = plugin.validate(minimal_data)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_difficulty(self, plugin):
        """無効な難易度のバリデーションテスト"""
        invalid_data = {
            "ingredients": [],
            "cooking_time": 30,
            "difficulty": "super_hard",  # 無効な値
            "servings": 2,
        }

        is_valid, errors = plugin.validate(invalid_data)
        assert is_valid is False
        assert any("difficulty" in error for error in errors)

    def test_validate_invalid_cooking_time(self, plugin):
        """無効な調理時間のバリデーションテスト"""
        invalid_data = {
            "ingredients": [],
            "cooking_time": 0,  # 0以下は無効
            "difficulty": "easy",
            "servings": 2,
        }

        is_valid, errors = plugin.validate(invalid_data)
        assert is_valid is False
        assert any("cooking_time" in error for error in errors)

    def test_validate_invalid_servings(self, plugin):
        """無効な人数分のバリデーションテスト"""
        invalid_data = {
            "ingredients": [],
            "cooking_time": 30,
            "difficulty": "medium",
            "servings": -1,  # 負の値は無効
        }

        is_valid, errors = plugin.validate(invalid_data)
        assert is_valid is False
        assert any("servings" in error for error in errors)

    def test_validate_invalid_rating(self, plugin):
        """無効な評価のバリデーションテスト"""
        # 範囲外（上限）
        invalid_data_upper = {
            "ingredients": [],
            "cooking_time": 30,
            "difficulty": "medium",
            "servings": 2,
            "rating": 5.5,  # 5.0より大きい
        }

        is_valid, errors = plugin.validate(invalid_data_upper)
        assert is_valid is False
        assert any("rating" in error for error in errors)

        # 範囲外（下限）
        invalid_data_lower = {
            "ingredients": [],
            "cooking_time": 30,
            "difficulty": "medium",
            "servings": 2,
            "rating": -0.5,  # 0.0より小さい
        }

        is_valid, errors = plugin.validate(invalid_data_lower)
        assert is_valid is False
        assert any("rating" in error for error in errors)

    def test_validate_missing_required_field(self, plugin):
        """必須フィールド欠落のバリデーションテスト"""
        incomplete_data = {
            "ingredients": [],
            # cooking_time が欠落
            "difficulty": "medium",
            "servings": 2,
        }

        is_valid, errors = plugin.validate(incomplete_data)
        assert is_valid is False
        assert any("cooking_time" in error for error in errors)

    def test_validate_type_mismatch(self, plugin):
        """型不一致のバリデーションテスト"""
        invalid_type_data = {
            "ingredients": "not a list",  # listであるべき
            "cooking_time": 30,
            "difficulty": "medium",
            "servings": 2,
        }

        is_valid, errors = plugin.validate(invalid_type_data)
        assert is_valid is False
        assert any("ingredients" in error for error in errors)

    def test_all_difficulty_levels(self, plugin):
        """すべての難易度レベルのテスト"""
        for difficulty in ["easy", "medium", "hard"]:
            data = {
                "ingredients": [],
                "cooking_time": 30,
                "difficulty": difficulty,
                "servings": 2,
            }
            is_valid, errors = plugin.validate(data)
            assert is_valid is True, f"difficulty '{difficulty}' should be valid"

    def test_rating_boundary_values(self, plugin):
        """評価の境界値テスト"""
        # 下限
        data_min = {
            "ingredients": [],
            "cooking_time": 30,
            "difficulty": "medium",
            "servings": 2,
            "rating": 0.0,
        }
        is_valid, _ = plugin.validate(data_min)
        assert is_valid is True

        # 上限
        data_max = {
            "ingredients": [],
            "cooking_time": 30,
            "difficulty": "medium",
            "servings": 2,
            "rating": 5.0,
        }
        is_valid, _ = plugin.validate(data_max)
        assert is_valid is True

    def test_nutrition_dict(self, plugin):
        """栄養情報の辞書テスト"""
        data_with_nutrition = {
            "ingredients": [],
            "cooking_time": 30,
            "difficulty": "medium",
            "servings": 2,
            "nutrition": {
                "calories": 500,
                "protein": 20,
                "carbs": 60,
                "fat": 15,
            },
        }

        is_valid, errors = plugin.validate(data_with_nutrition)
        assert is_valid is True
        assert len(errors) == 0
