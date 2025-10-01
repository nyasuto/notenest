"""メタデータパーサーのテスト"""

from notenest.core.metadata import MetadataParser, WikiLinkParser


def test_parse_frontmatter():
    """Frontmatterの解析テスト"""
    content = """---
title: Test Page
tags: [tag1, tag2]
---

# Content

This is test content.
"""

    metadata, body = MetadataParser.parse(content)

    assert metadata["title"] == "Test Page"
    assert metadata["tags"] == ["tag1", "tag2"]
    assert "# Content" in body


def test_serialize_frontmatter():
    """Frontmatterのシリアライズテスト"""
    metadata = {"title": "Test", "tags": ["a", "b"]}
    content = "# Test"

    result = MetadataParser.serialize(metadata, content)

    assert "---" in result
    assert "title: Test" in result
    assert "# Test" in result


def test_extract_wiki_links():
    """Wiki Linkの抽出テスト"""
    content = """
    This is a [[link1]] and [[link2]].
    Also [[display|page-slug]] format.
    """

    links = WikiLinkParser.extract_links(content)

    assert "link1" in links
    assert "link2" in links
    assert "page-slug" in links
    assert len(links) == 3
