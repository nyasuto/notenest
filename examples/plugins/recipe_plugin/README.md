# Recipe Plugin

レシピ管理用のメタデータプラグインです。料理のレシピ情報を構造化して管理できます。

## 機能

- 材料リストの管理
- 調理時間の記録
- 難易度の設定
- 人数分の指定
- 栄養情報の記録
- 評価機能

## メタデータフィールド

| フィールド名 | 型 | 必須 | デフォルト | 説明 |
|------------|-----|------|-----------|------|
| `ingredients` | `list` | ✓ | `[]` | 材料リスト |
| `cooking_time` | `int` | ✓ | `30` | 調理時間（分） |
| `difficulty` | `str` | ✓ | `"medium"` | 難易度（`easy`, `medium`, `hard`） |
| `servings` | `int` | ✓ | `2` | 何人分か |
| `nutrition` | `dict` | | `{}` | 栄養情報（カロリー、タンパク質など） |
| `rating` | `float` | | `None` | 評価（0.0～5.0） |

## 使い方

### プラグインの登録

```python
from notenest.plugins.registry import get_global_registry
from examples.plugins.recipe_plugin import RecipePlugin

# プラグインを登録
registry = get_global_registry()
registry.register(RecipePlugin())
```

### レシピページの作成

```python
from notenest.core.repository import Repository

repo = Repository(workspace_path)

# レシピページを作成
recipe_page = repo.create_page(
    slug="pasta-carbonara",
    title="カルボナーラ",
    content="""# カルボナーラ

## 作り方

1. パスタを茹でる
2. ベーコンを炒める
3. 卵液を作る
4. すべてを混ぜ合わせる
5. 完成！
""",
    metadata={
        "metadata_type": "recipe",
        "ingredients": [
            "スパゲッティ 200g",
            "ベーコン 100g",
            "卵 2個",
            "パルメザンチーズ 50g",
            "黒胡椒 適量",
        ],
        "cooking_time": 20,
        "difficulty": "medium",
        "servings": 2,
        "nutrition": {
            "calories": 650,
            "protein": 28,
            "carbs": 75,
            "fat": 25,
        },
        "rating": 4.5,
    }
)
```

## サンプルレシピ

`examples/recipes/` ディレクトリにサンプルレシピが用意されています：

- カレーライス
- カルボナーラ
- チョコレートケーキ

## バリデーションルール

### 難易度（difficulty）
- 許可される値: `"easy"`, `"medium"`, `"hard"`

### 調理時間（cooking_time）
- 0より大きい整数

### 人数分（servings）
- 0より大きい整数

### 評価（rating）
- 0.0以上5.0以下の数値

## 拡張例

このプラグインは拡張可能です。例えば：

- レシピカタログ機能（全レシピの一覧表示）
- 栄養情報の自動計算
- 材料の在庫管理との連携
- 調理手順のステップ管理

これらの機能は `on_page_create`, `on_page_update`, `on_page_delete` フックを使って実装できます。
