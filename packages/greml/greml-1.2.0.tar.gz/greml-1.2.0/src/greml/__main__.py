import sys
import warnings
from enum import Enum
from urllib.parse import urlparse

import httpx
import typer
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from click import ClickException, UsageError
from fake_useragent import UserAgent
from rich.console import Console
from soupsieve.util import SelectorSyntaxError

from greml.__version__ import version_callback

warnings.filterwarnings("error")

app = typer.Typer()
console = Console()
err_console = Console(stderr=True)


class ExitCodes:
    NO_STDIN_DATA = 10
    HTTP_GET_ERROR = 11
    FILE_READ_ERROR = 12
    NOT_MARKUP = 13
    SELECTOR_ERROR = 14


class Error(ClickException):
    def __init__(self, message: str, exit_code=1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class InputType(Enum):
    STDIN = "stdin"
    FILE = "file"
    HTTP = "http"


def type_of_input(input_path):
    if not input_path:
        return InputType.STDIN

    try:
        parsed_url = urlparse(input_path)
    except Exception:
        return InputType.FILE

    if parsed_url.scheme:
        if parsed_url.scheme in ["http", "https"]:
            return InputType.HTTP
    else:
        return InputType.FILE


def get_stdin():
    try:
        data = sys.stdin.buffer.read()
        if not data:
            raise Error("No data on stdin. Please provide input.", ExitCodes.NO_STDIN_DATA)
        return data.decode()
    except Exception:
        raise Error("No data on stdin. Please provide input.", ExitCodes.NO_STDIN_DATA)


def get_http(url, follow_redirects, user_agent=None, timeout=30):
    try:
        headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        return httpx.get(url, follow_redirects=follow_redirects, headers=headers, timeout=timeout).text
    except httpx.ConnectError:
        raise Error("Connect error", ExitCodes.HTTP_GET_ERROR)
    except httpx.TimeoutException:
        raise Error(f"Request timed out after {timeout} seconds", ExitCodes.HTTP_GET_ERROR)


def get_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise Error(f"File '{path}' not found", ExitCodes.FILE_READ_ERROR)


def display_callback(value):
    if value in ["text", "json", "html"]:
        return value, None
    if value.startswith("attr."):
        attr = value.split(".")
        return attr[0], "".join(attr[1:])
    raise typer.BadParameter("Must be 'text', 'json', 'html' or 'attr.ATTR'")


@app.command()
def main(  # noqa: PLR0913
    input_path: str = typer.Argument(
        None, help="Input file path or URL. If not specified uses stdin.", show_default="stdin"
    ),
    selector: str = typer.Argument(None, help="HTML selector"),
    display: str = typer.Option(
        "text", help="How to display, either 'text', 'json', 'html' or 'attr.ATTR'", callback=display_callback
    ),
    follow_redirects: bool = typer.Option(True, "--follow-redirects/--no-follow-redirects"),
    user_agent: str = typer.Option(None, "--user-agent", help="Custom User-Agent header for HTTP requests"),
    user_agent_random: bool = typer.Option(False, "--user-agent-random", help="Use a random User-Agent header"),
    timeout: int = typer.Option(30, "--timeout", help="Timeout in seconds for HTTP requests"),
    _: bool = typer.Option(None, "-v", "--version", callback=version_callback, is_eager=True),
):
    # input_path should be optional and default to stdin. If it's set but the selector isn't then swap them around
    if selector is None and input_path is not None:
        selector = input_path
        input_path = None

    # Get display method and the name of the attr if desired
    display, attr = display[0], display[1]

    if not selector:
        raise UsageError("No selector provided")

    if user_agent and user_agent_random:
        raise UsageError("Cannot use both --user-agent and --user-agent-random")

    input_type = type_of_input(input_path)

    if user_agent_random:
        ua = UserAgent()
        user_agent = ua.random

    if input_type == InputType.STDIN:
        html_doc = get_stdin()
    elif input_type == InputType.HTTP:
        html_doc = get_http(input_path, follow_redirects, user_agent, timeout)
    elif input_type == InputType.FILE:
        html_doc = get_file(input_path)

    try:
        soup = BeautifulSoup(html_doc, "html.parser")
    except MarkupResemblesLocatorWarning:
        raise Error("Markup resembles a locator rather than content", ExitCodes.NOT_MARKUP)

    try:
        elements = soup.select(selector)
    except SelectorSyntaxError as exc:
        raise Error(f"Unable to parse selector:\n{exc.context}", ExitCodes.SELECTOR_ERROR)

    json_data = []
    for element in elements:
        if display == "text":
            if element_text := element.get_text():
                print(element_text.strip())
        elif display == "json":
            element_json = {"text": element.get_text()}
            element_json.update(element.attrs)
            json_data.append(element_json)
        elif display == "html":
            print(str(element))
        elif display == "attr":
            if element_attr := element.get(attr):
                print(element_attr)

    if display == "json":
        console.print_json(data=json_data)


if __name__ == "__main__":
    app()
