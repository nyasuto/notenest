"""エントリーポイント"""

import argparse
from pathlib import Path

from notenest.ui.app import NoteNestApp


def main() -> None:
    """メイン関数"""
    parser = argparse.ArgumentParser(description="NoteNest - マークダウンベース ナレッジベース・Wikiシステム")
    parser.add_argument(
        "workspace",
        nargs="?",
        default=".",
        help="ワークスペースディレクトリ（デフォルト: カレントディレクトリ）",
    )

    args = parser.parse_args()
    workspace_path = Path(args.workspace).resolve()

    # TUIアプリ起動
    app = NoteNestApp(workspace_path)
    app.run()


if __name__ == "__main__":
    main()
