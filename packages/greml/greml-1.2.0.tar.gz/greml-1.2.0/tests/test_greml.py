import pytest
from click.exceptions import UsageError
from typer.testing import CliRunner

from greml.__main__ import ExitCodes, app

runner = CliRunner(mix_stderr=False)


def run(*args):
    return runner.invoke(app, [*args])


@pytest.mark.parametrize(
    "selector,expected",
    [
        ("title", "HTML - Wikipedia\n"),
        (
            "#mw-content-text > div.mw-content-ltr.mw-parser-output > div:nth-child(3)",
            '".htm" and ".html" redirect here. For other uses, see HTM.\n',
        ),
        (
            "[accesskey]",
            "Main page\nRandom article\nRecent changes\nSearch\nLog in\nLog in\nContributions\nTalk\nArticle\nTalk\nView source\nView history\nWhat links here\nRelated changes\nUpload file\nSpecial pages\nWikidata item\nPrintable version\n",
        ),
        (".infobox-caption", "The official logo of the latest version, HTML5[1]\n"),
        (".missing-class", ""),
    ],
)
def test_wikipedia_text(selector, expected):
    result = run("tests/data/wikipedia_html.html", selector)
    assert result.stdout == expected


@pytest.mark.parametrize(
    "selector,attr,expected",
    [
        ('meta[name="robots"]', "content", "max-image-preview:standard\n"),
        (
            '[href*="ietf"]',
            "href",
            "https://datatracker.ietf.org/doc/html/rfc1866\nhttps://datatracker.ietf.org/doc/html/rfc1867\nhttps://datatracker.ietf.org/doc/html/rfc1942\nhttps://datatracker.ietf.org/doc/html/rfc1980\nhttps://datatracker.ietf.org/doc/html/rfc2070\n#cite_note-ietfiiir-38\nhttps://datatracker.ietf.org/doc/html/rfc1866\nhttps://www.w3.org/MarkUp/draft-ietf-iiir-html-01.txt\nhttps://web.archive.org/web/20170103041713/https://www.w3.org/MarkUp/draft-ietf-iiir-html-01.txt\nhttp://tools.ietf.org/html/rfc1866\nhttps://tools.ietf.org/html/rfc1866\nhttps://web.archive.org/web/20100811072528/http://tools.ietf.org/html/rfc1866\nhttp://tools.ietf.org/html/draft-ietf-iiir-html-00\n#cite_ref-ietfiiir_38-0\nhttps://www.w3.org/MarkUp/draft-ietf-iiir-html-01.txt\nhttps://datatracker.ietf.org/doc/draft-raggett-www-html/history/\nhttp://tools.ietf.org/html/draft-ietf-html-spec-00\nhttps://tools.ietf.org/html/draft-ietf-html-spec-02#section-1.1\nhttps://datatracker.ietf.org/doc/rfc1866/history/\nhttp://www.ietf.org/rfc/rfc2119.txt\nhttps://tools.ietf.org/html/rfc2119\n",
        ),
    ],
)
def test_wikipedia_attr(selector, attr, expected):
    result = run("tests/data/wikipedia_html.html", "--display", f"attr.{attr}", selector)
    assert result.stdout == expected


@pytest.mark.parametrize(
    "selector,expected",
    [
        (
            ".mw-page-title-main",
            '[\n  {\n    "text": "HTML",\n    "class": [\n      "mw-page-title-main"\n    ]\n  }\n]\n',
        ),
        (
            ".mw-headline",
            '[\n  {\n    "text": "History",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "History"\n  },\n  {\n    "text": "Development",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Development"\n  },\n  {\n    "text": "HTML version timeline",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTML_version_timeline"\n  },\n  {\n    "text": "HTML 2",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTML_2"\n  },\n  {\n    "text": "HTML 3",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTML_3"\n  },\n  {\n    "text": "HTML 4",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTML_4"\n  },\n  {\n    "text": "HTML 5",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTML_5"\n  },\n  {\n    "text": "HTML draft version timeline",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTML_draft_version_timeline"\n  },\n  {\n    "text": "XHTML versions",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "XHTML_versions"\n  },\n  {\n    "text": "Transition of HTML Publication to WHATWG",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Transition_of_HTML_Publication_to_WHATWG"\n  },\n  {\n    "text": "Markup",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Markup"\n  },\n  {\n    "text": "Elements",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Elements"\n  },\n  {\n    "text": "Element examples",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Element_examples"\n  },\n  {\n    "text": "Headings",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Headings"\n  },\n  {\n    "text": "Line breaks",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Line_breaks"\n  },\n  {\n    "text": "Inputs",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Inputs"\n  },\n  {\n    "text": "Attributes",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Attributes"\n  },\n  {\n    "text": "Character and entity references",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Character_and_entity_references"\n  },\n  {\n    "text": "Data types",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Data_types"\n  },\n  {\n    "text": "Document type declaration",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Document_type_declaration"\n  },\n  {\n    "text": "Semantic HTML",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Semantic_HTML"\n  },\n  {\n    "text": "Delivery",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Delivery"\n  },\n  {\n    "text": "HTTP",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTTP"\n  },\n  {\n    "text": "HTML e-mail",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTML_e-mail"\n  },\n  {\n    "text": "Naming conventions",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Naming_conventions"\n  },\n  {\n    "text": "HTML Application",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTML_Application"\n  },\n  {\n    "text": "HTML4 variations",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "HTML4_variations"\n  },\n  {\n    "text": "SGML-based versus XML-based HTML",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "SGML-based_versus_XML-based_HTML"\n  },\n  {\n    "text": "Transitional versus strict",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Transitional_versus_strict"\n  },\n  {\n    "text": "Frameset versus transitional",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Frameset_versus_transitional"\n  },\n  {\n    "text": "Summary of specification versions",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "Summary_of_specification_versions"\n  },\n  {\n    "text": "WHATWG HTML versus HTML5",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "WHATWG_HTML_versus_HTML5"\n  },\n  {\n    "text": "WYSIWYG editors",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "WYSIWYG_editors"\n  },\n  {\n    "text": "See also",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "See_also"\n  },\n  {\n    "text": "References",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "References"\n  },\n  {\n    "text": "External links",\n    "class": [\n      "mw-headline"\n    ],\n    "id": "External_links"\n  }\n]\n',
        ),
    ],
)
def test_wikipedia_json(selector, expected):
    result = run("tests/data/wikipedia_html.html", "--display", "json", selector)
    assert result.stdout == expected


@pytest.mark.parametrize(
    "selector,expected",
    [
        (
            ".mw-page-title-main",
            '<span class="mw-page-title-main">HTML</span>\n',
        ),
        (
            'meta[name="robots"]',
            '<meta content="max-image-preview:standard" name="robots"/>\n',
        ),
        (
            ".infobox-caption",
            '<div class="infobox-caption">The official logo of the latest version, <a href="/wiki/HTML5" title="HTML5">HTML5</a><sup class="reference" id="cite_ref-1"><a href="#cite_note-1">[1]</a></sup></div>\n',
        ),
        (".missing-class", ""),
    ],
)
def test_wikipedia_html(selector, expected):
    result = run("tests/data/wikipedia_html.html", "--display", "html", selector)
    assert result.stdout == expected


def test_http_text():
    result = run("https://no-spoilers.wiki/", "title")
    assert result.stdout == "Wikipedia without Spoilers!\n"


def test_file_error():
    result = run("file/does/not/exist", ".ignored")
    assert "File 'file/does/not/exist' not found" in result.stderr
    assert result.exit_code == ExitCodes.FILE_READ_ERROR


def test_http_error():
    result = run("http://some-url-that-does-not-exist.local", ".ignored")
    assert "Connect error" in result.stderr
    assert result.exit_code == ExitCodes.HTTP_GET_ERROR


def test_http_rediect():
    result_redirect = run("https://httpbin.org/redirect-to?url=https%3A%2F%2Fgithub.com&status_code=302", "title")
    result_no_redirect = run(
        "https://httpbin.org/redirect-to?url=https%3A%2F%2Fgithub.com&status_code=302", "title", "--no-follow-redirects"
    )
    assert "GitHub" in result_redirect.stdout
    assert "GitHub" not in result_no_redirect.stdout


def test_user_agent():
    result = run(
        "https://www.whatismybrowser.com/detect/what-is-my-user-agent/", "#detected_value", "--user-agent", "greml"
    )
    assert "greml" in result.stdout


def test_user_agent_conflict():
    result = run("https://example.com", "title", "--user-agent", "test-agent", "--user-agent-random")
    assert result.exit_code == UsageError.exit_code
    assert "Cannot use both" in result.stderr


def test_user_agent_random():
    result = run(
        "https://www.whatismybrowser.com/detect/what-is-my-user-agent/", "#detected_value", "--user-agent-random"
    )
    # Should not contain 'python' or 'httpx' (default user agents)
    assert "python" not in result.stdout.lower()
    assert "httpx" not in result.stdout.lower()
    # Should contain some browser identifier
    assert any(browser in result.stdout.lower() for browser in ["chrome", "firefox", "safari", "edge"])


def test_http_timeout():
    # Test that a request times out after 1 second when hitting a 2-second delay endpoint
    result = run("https://httpbin.org/delay/2", "title", "--timeout", "1")
    assert "Request timed out after 1 seconds" in result.stderr
    assert result.exit_code == ExitCodes.HTTP_GET_ERROR

    # Test that a request succeeds when timeout is longer than the delay
    result = run("https://httpbin.org/delay/1", "title", "--timeout", "5")
    assert result.exit_code == 0
