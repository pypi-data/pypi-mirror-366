# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import re
import typing
from pathlib import Path

import frontmatter
import msgspec
import yaml

from .models import Document, Section

RE_HEADER = re.compile(r"^(?P<header>[#]+)[ ]+(?P<text>.+)$")


def load_document(file: typing.IO):
    return msgspec.yaml.decode(file.read(), type=Document)


def clamp_header_level(header_level: int) -> int:
    return max(1, min(6, header_level))


def build_header(level: int, text: str) -> str:
    return "{header} {text}".format(header="#" * level, text=text)


def compute_header_level_adjustment(
    lines: typing.List[str], starting_level: int = 1
) -> int:
    minimum_header_level = None
    for line in lines:
        if line.startswith("#"):
            match = RE_HEADER.match(line)
            if match:
                header_level = clamp_header_level(len(match.group("header")))
                if minimum_header_level is None:
                    minimum_header_level = header_level
                else:
                    minimum_header_level = min(minimum_header_level, header_level)

    if minimum_header_level is None:
        minimum_header_level = starting_level

    target_level = starting_level + 1
    level_adjustment = target_level - minimum_header_level
    return level_adjustment


def adjust_header_level(content: str, starting_level: int = 1) -> str:
    lines = content.splitlines()

    level_adjustment = compute_header_level_adjustment(
        lines=lines, starting_level=starting_level
    )

    newlines = []
    for line in lines:
        newline = line
        if line.startswith("#"):
            match = RE_HEADER.match(line)
            if match:
                header_level = clamp_header_level(
                    len(match.group("header")) + level_adjustment
                )
                newline = build_header(header_level, match.group("text"))
        newlines.append(newline)
    return "\n".join(newlines)


def build_page_blocks(text: str, starting_level: int = 1) -> typing.List[str]:
    metadata, content = frontmatter.parse(text)
    content = adjust_header_level(content, starting_level=starting_level)
    return [
        build_header(level=starting_level, text=metadata["title"]),
        content.rstrip(),
    ]


def build_section_blocks(
    doc_dir: Path, section: Section, starting_level: int = 1
) -> typing.List[str]:
    if isinstance(section, str):
        return build_page_blocks(
            open(doc_dir / section).read(), starting_level=starting_level
        )
    blocks = [build_header(level=starting_level, text=section.title)]
    for subsection in section.sections:
        blocks.extend(
            build_section_blocks(doc_dir, subsection, starting_level=starting_level + 1)
        )
    return blocks


def filter_metadata(
    metadata: typing.Dict[str, typing.Any],
) -> typing.Dict[str, typing.Any]:
    return {
        key: value
        for key, value in metadata.items()
        if key
        not in (
            "title",
            "version",
        )
    }


def build_document(doc_dir: Path, document: Document) -> str:
    content = "\n\n".join(
        [
            block
            for section in document.sections
            for block in build_section_blocks(doc_dir, section)
        ]
    )

    metadata = filter_metadata(document.metadata)

    output = ""
    output += "---\n"

    output += yaml.dump(
        dict(
            title=document.title,
            version=document.version,
        )
    )

    if metadata:
        output += "\n# metadata\n"
        output += yaml.dump(metadata)

    output += "---\n\n"

    output += content + "\n"

    return output
