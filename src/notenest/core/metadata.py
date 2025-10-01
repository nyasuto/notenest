"""メタデータ処理"""

import re
from collections.abc import Callable
from typing import Any

import frontmatter
import yaml


class MetadataParser:
    """Frontmatter（YAML）パーサー"""

    @staticmethod
    def parse(content: str) -> tuple[dict[str, Any], str]:
        """
        マークダウンからFrontmatterとコンテンツを分離

        Args:
            content: マークダウンテキスト

        Returns:
            (metadata, content) のタプル
        """
        try:
            post = frontmatter.loads(content)
            return dict(post.metadata), post.content
        except Exception:
            # Frontmatterがない場合は空の辞書を返す
            return {}, content

    @staticmethod
    def serialize(metadata: dict[str, Any], content: str) -> str:
        """
        メタデータとコンテンツをマークダウンに結合

        Args:
            metadata: メタデータ辞書
            content: マークダウン本文

        Returns:
            Frontmatter付きマークダウンテキスト
        """
        if not metadata:
            return content

        yaml_str = yaml.dump(metadata, allow_unicode=True, sort_keys=False)
        return f"---\n{yaml_str}---\n\n{content}"


class WikiLinkParser:
    """Wiki Link（[[ページ名]]）パーサー"""

    WIKI_LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")

    @classmethod
    def extract_links(cls, content: str) -> list[str]:
        """
        コンテンツからWiki Linkを抽出

        Args:
            content: マークダウンテキスト

        Returns:
            リンク先ページslugのリスト
        """
        matches = cls.WIKI_LINK_PATTERN.findall(content)
        # [[表示名|ページ名]] 形式にも対応
        links = []
        for match in matches:
            if "|" in match:
                # 表示名とページ名が分離されている場合
                _, slug = match.split("|", 1)
                links.append(slug.strip())
            else:
                links.append(match.strip())
        return links

    @classmethod
    def replace_links(cls, content: str, replacer: Callable[[str, str], str]) -> str:
        """
        Wiki Linkを置換

        Args:
            content: マークダウンテキスト
            replacer: リンク先slugを受け取り、置換後の文字列を返す関数

        Returns:
            置換後のマークダウンテキスト
        """

        def replace_func(match: re.Match[str]) -> str:
            link_text = match.group(1)
            if "|" in link_text:
                display, slug = link_text.split("|", 1)
                return replacer(slug.strip(), display.strip())
            else:
                return replacer(link_text.strip(), link_text.strip())

        return cls.WIKI_LINK_PATTERN.sub(replace_func, content)
