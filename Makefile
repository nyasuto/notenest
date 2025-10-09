.PHONY: help setup install test format lint typecheck quality clean run demo dev-setup web-api web-dev web-build web-install

# デフォルトターゲット
.DEFAULT_GOAL := help

help: ## ヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## 開発環境のセットアップ（仮想環境作成 + 依存関係インストール）
	uv venv
	uv pip install -e ".[dev]"
	@echo "✅ Setup complete! Run 'source .venv/bin/activate' to activate the virtual environment."

install: ## 依存関係のインストール（仮想環境が既にある場合）
	uv pip install -e ".[dev]"

test: ## テストを実行
	@if [ -d .venv ]; then \
		. .venv/bin/activate && pytest; \
	else \
		pytest; \
	fi

test-v: ## テストを詳細表示で実行
	@if [ -d .venv ]; then \
		. .venv/bin/activate && pytest -v; \
	else \
		pytest -v; \
	fi

test-cov: ## テストをカバレッジレポート付きで実行
	@if [ -d .venv ]; then \
		. .venv/bin/activate && pytest --cov=src/notenest --cov-report=html --cov-report=term --cov-report=xml; \
	else \
		pytest --cov=src/notenest --cov-report=html --cov-report=term --cov-report=xml; \
	fi

format: ## コードフォーマット（ruff）
	@if [ -d .venv ]; then \
		. .venv/bin/activate && ruff format src/ tests/; \
	else \
		ruff format src/ tests/; \
	fi

format-check: ## コードフォーマットチェック（変更なし）
	@if [ -d .venv ]; then \
		. .venv/bin/activate && ruff format --check src/ tests/; \
	else \
		ruff format --check src/ tests/; \
	fi

lint: ## リント（ruff）
	@if [ -d .venv ]; then \
		. .venv/bin/activate && ruff check src/ tests/; \
	else \
		ruff check src/ tests/; \
	fi

lint-fix: ## リント自動修正
	@if [ -d .venv ]; then \
		. .venv/bin/activate && ruff check --fix src/ tests/; \
	else \
		ruff check --fix src/ tests/; \
	fi

typecheck: ## 型チェック（mypy）
	@if [ -d .venv ]; then \
		. .venv/bin/activate && mypy src/; \
	else \
		mypy src/; \
	fi

quality: format-check lint typecheck test ## 全品質チェック（CI用）

clean: ## 生成ファイルを削除
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build/ dist/ htmlcov/ .coverage
	@echo "✅ Cleaned up generated files"

clean-demo: ## デモディレクトリのDBを削除
	rm -rf demo/.notenest/
	@echo "✅ Demo database cleaned"

run: ## NoteNestを起動（カレントディレクトリ）
	python -m notenest

demo: ## デモデータでNoteNestを起動
	python -m notenest demo

# Web GUI関連
web-install: ## フロントエンドの依存関係をインストール
	cd src/web/frontend && npm install

web-api: ## APIサーバーを起動（ポート8000）
	@echo "Checking for processes on port 8000..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@sleep 1
	@if [ -d .venv ]; then \
		. .venv/bin/activate && uvicorn web.api.main:app --reload --host 0.0.0.0 --port 8000; \
	else \
		uvicorn web.api.main:app --reload --host 0.0.0.0 --port 8000; \
	fi

web-dev: ## フロントエンド開発サーバーを起動（ポート5173）
	@echo "Checking for processes on port 5173..."
	@lsof -ti:5173 | xargs kill -9 2>/dev/null || true
	@sleep 1
	cd src/web/frontend && npm run dev

web-build: ## フロントエンドをビルド
	cd src/web/frontend && npm run build

serve: web-build ## 本番モードで起動（1サーバー、ポート8000）
	@echo "Building frontend..."
	@echo "Checking for processes on port 8000..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@sleep 1
	@echo "Starting NoteNest server on http://localhost:8000"
	@if [ -d .venv ]; then \
		. .venv/bin/activate && uvicorn web.api.main:app --host 0.0.0.0 --port 8000; \
	else \
		uvicorn web.api.main:app --host 0.0.0.0 --port 8000; \
	fi

dev-setup: setup ## 開発環境の完全セットアップ（setup + 品質チェック）
	@echo "Running quality checks..."
	$(MAKE) quality
	@echo "✅ Development environment is ready!"

watch-test: ## テストを監視モードで実行（pytest-watch必要）
	ptw

# Git関連
branch: ## 現在のブランチを表示
	@git branch --show-current

status: ## Gitステータスを表示
	@git status

# ドキュメント
docs: ## ドキュメントを表示
	@echo "📚 Available documentation:"
	@echo "  - README.md: Project overview"
	@echo "  - QUICKSTART.md: Quick start guide"
	@echo "  - docs/setup.md: Setup instructions"
	@echo "  - docs/usage.md: Usage guide"

# プロジェクト情報
info: ## プロジェクト情報を表示
	@echo "📦 Project: NoteNest"
	@echo "🐍 Python version: $$(python --version)"
	@echo "📍 Branch: $$(git branch --show-current)"
	@echo "📊 Files: $$(find src/ -name '*.py' | wc -l | tr -d ' ') Python files"
	@echo "🧪 Tests: $$(find tests/ -name 'test_*.py' | wc -l | tr -d ' ') test files"
