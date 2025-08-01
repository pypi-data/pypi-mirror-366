import argparse
import dataclasses
import json
import pathlib
from typing import List

from markdown_it import MarkdownIt
from markdown_it.token import Token


@dataclasses.dataclass
class LobsterFileReference:
    file: str
    line: int | None
    column: int | None
    kind: str = "file"


@dataclasses.dataclass
class LobsterActivity:
    tag: str
    location: LobsterFileReference
    name: str
    refs: List[str]
    just_up: List[str]
    just_down: List[str]
    just_global: List[str]
    framework: str
    kind: str
    status: str | None


@dataclasses.dataclass
class Lobster:
    data: List[LobsterActivity] = dataclasses.field(default_factory=list)
    schema: str = "lobster-act-trace"
    version: int = 3
    generator: str = "md2lobster"


def have_link(token: Token):
    if token.type == "link_open":
        return True
    else:
        if token.children:
            return any(map(have_link, token.children))
        else:
            return False


def get_link(token: Token):
    if token.type == "link_open":
        return token.attrs["href"].replace("_", " ", 1)
    else:
        if token.children:
            for child in token.children:
                lnk = get_link(child)
                if lnk:
                    return lnk
        else:
            return None


def get_text(token: Token):
    if token.type == "text":
        return token.content
    else:
        if token.children:
            for child in token.children:
                txt = get_text(child)
                if txt:
                    return txt
        else:
            return None


def get_line(token: Token):
    if token.type == "inline":
        return token.map[0] + 1  # We don't consider the first line to be line 0
    else:
        if token.children:
            for child in token.children:
                line = get_line(child)
                if line:
                    return line
        else:
            return None


def process_token(
    token: Token, lobster: Lobster, file_name: pathlib.Path, framework, kind
):
    if have_link(token):
        text = get_text(token)
        activity = LobsterActivity(
            "markdown " + text.replace(" ", "_"),
            LobsterFileReference(file_name.name, get_line(token), None),
            text,
            [get_link(token)],
            [],
            [],
            [],
            framework,
            kind,
            None,
        )
        lobster.data.append(activity)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        help="Markdown input file",
        type=pathlib.Path,
    )
    parser.add_argument(
        "--output",
        help="Lobster output file",
        type=pathlib.Path,
        default=pathlib.Path("markdown.lobster"),
    )
    parser.add_argument(
        "--framework",
        help="Framework for lobster activity",
        type=str,
        default="markdown",
    )
    parser.add_argument(
        "--kind",
        help="Kind for lobster activity",
        type=str,
        default="Test",
    )
    return parser.parse_args()


def main():
    md = MarkdownIt()
    args = parse_args()
    with args.input.open("r") as input:
        lobster = Lobster()
        for token in md.parse(input.read()):
            process_token(token, lobster, args.input, args.framework, args.kind)
        lobster_json = json.dumps(dataclasses.asdict(lobster))
        with args.output.open("w") as output:
            output.write(lobster_json)


if __name__ == "__main__":
    main()
