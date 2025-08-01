from unittest.mock import Mock

from markdown_it import MarkdownIt

from md2lobster.md2lobster import Lobster, process_token


def test_no_link():
    md = MarkdownIt()
    lobster = Lobster()
    for token in md.parse("some *text*"):
        process_token(token, lobster, "input", "framework", "Test")
    assert len(lobster.data) == 0


def test_with_link():
    md = MarkdownIt()
    lobster = Lobster()
    input = "[test_report tag1](req_System.simply_the_best)"
    mockfile = Mock()
    mockfile.name = "input"
    for token in md.parse(input):
        process_token(token, lobster, mockfile, "framework", "Test")
    assert len(lobster.data) == 1


def test_links_and_header():
    md = MarkdownIt()
    lobster = Lobster()
    input = """
### Part
[test_report tag1](req_System.simply_the_best)
Some more text
"""
    mockfile = Mock()
    mockfile.name = "input"
    for token in md.parse(input):
        process_token(token, lobster, mockfile, "framework", "Test")
    assert len(lobster.data) == 1
