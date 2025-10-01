"""エクスポート機能"""

import json
from pathlib import Path
from typing import Any

import markdown

from notenest.core.page import Page


class Exporter:
    """ページのエクスポート機能"""

    @staticmethod
    def export_to_html(page: Page, output_path: Path | None = None) -> str:
        """
        ページをHTMLにエクスポート

        Args:
            page: エクスポート対象のページ
            output_path: 出力先パス（Noneの場合は文字列を返すのみ）

        Returns:
            str: 生成されたHTML
        """
        # マークダウンをHTMLに変換
        md = markdown.Markdown(extensions=["extra", "codehilite", "toc"])
        content_html = md.convert(page.content)

        # HTMLテンプレート
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page.title}</title>
    <style>
        body {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
        }}
        h1, h2, h3 {{
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        code {{
            background-color: #f6f8fa;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        .metadata {{
            background-color: #f0f0f0;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 24px;
        }}
        .tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .tag {{
            background-color: #0969da;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <article>
        <div class="metadata">
            <h1>{page.title}</h1>
            <p><strong>Slug:</strong> {page.slug}</p>
            <p><strong>Type:</strong> {page.metadata_type}</p>
            <p><strong>Created:</strong> {page.created_at.strftime("%Y-%m-%d %H:%M") if page.created_at else "N/A"}</p>
            <p><strong>Updated:</strong> {page.updated_at.strftime("%Y-%m-%d %H:%M") if page.updated_at else "N/A"}</p>
            <div class="tags">
                {"".join(f'<span class="tag">{tag}</span>' for tag in page.tags)}
            </div>
        </div>
        {content_html}
    </article>
</body>
</html>"""

        # ファイル出力
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")

        return html

    @staticmethod
    def export_all_to_html(pages: list[Page], output_dir: Path) -> list[Path]:
        """
        全ページをHTMLにエクスポート

        Args:
            pages: エクスポート対象のページリスト
            output_dir: 出力先ディレクトリ

        Returns:
            list: 生成されたHTMLファイルのパスリスト
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_files = []

        for page in pages:
            output_path = output_dir / f"{page.slug}.html"
            Exporter.export_to_html(page, output_path)
            output_files.append(output_path)

        # インデックスページ生成
        index_html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NoteNest - Index</title>
    <style>
        body {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        }
        ul { list-style-type: none; padding: 0; }
        li { margin: 12px 0; }
        a { text-decoration: none; color: #0969da; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>NoteNest - Index</h1>
    <ul>
"""
        for page in sorted(pages, key=lambda p: p.title):
            index_html += f'        <li><a href="{page.slug}.html">{page.title}</a></li>\n'

        index_html += """    </ul>
</body>
</html>"""

        index_path = output_dir / "index.html"
        index_path.write_text(index_html, encoding="utf-8")
        output_files.append(index_path)

        return output_files

    @staticmethod
    def export_to_json(page: Page, output_path: Path | None = None) -> str:
        """
        ページをJSONにエクスポート

        Args:
            page: エクスポート対象のページ
            output_path: 出力先パス（Noneの場合は文字列を返すのみ）

        Returns:
            str: 生成されたJSON
        """
        data: dict[str, Any] = {
            "slug": page.slug,
            "title": page.title,
            "content": page.content,
            "tags": page.tags,
            "metadata_type": page.metadata_type,
            "metadata": page.metadata,
            "created_at": page.created_at.isoformat() if page.created_at else None,
            "updated_at": page.updated_at.isoformat() if page.updated_at else None,
        }

        json_str = json.dumps(data, ensure_ascii=False, indent=2)

        # ファイル出力
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json_str, encoding="utf-8")

        return json_str

    @staticmethod
    def export_all_to_json(pages: list[Page], output_path: Path) -> Path:
        """
        全ページをJSONにエクスポート

        Args:
            pages: エクスポート対象のページリスト
            output_path: 出力先ファイルパス

        Returns:
            Path: 生成されたJSONファイルのパス
        """
        data = {
            "pages": [
                {
                    "slug": page.slug,
                    "title": page.title,
                    "content": page.content,
                    "tags": page.tags,
                    "metadata_type": page.metadata_type,
                    "metadata": page.metadata,
                    "created_at": page.created_at.isoformat() if page.created_at else None,
                    "updated_at": page.updated_at.isoformat() if page.updated_at else None,
                }
                for page in pages
            ],
            "export_date": Path.cwd().as_posix(),
            "total_pages": len(pages),
        }

        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_str, encoding="utf-8")

        return output_path
