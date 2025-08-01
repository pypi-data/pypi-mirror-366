# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Taneli Hukkinen
# Licensed to PSF under a Contributor Agreement.

import re
import string
from typing import Any, BinaryIO, Dict, List, Optional, TextIO, Union

from ._re import (
    RE_DATETIME,
    RE_LOCALTIME,
    RE_NUMBER,
    match_to_datetime,
    match_to_localtime,
    match_to_number,
)
from ._types import Key, ParseFloat, Pos

ASCII_CTRL = frozenset(chr(i) for i in range(32)) | {chr(127)}
ILLEGAL_BASIC_STR_CHARS = ASCII_CTRL - {"\t"}
BARE_KEY_CHARS = frozenset(string.ascii_letters + string.digits + "-_")
BASIC_STR_ESCAPE_REPLACEMENTS = {
    "\\b": "\b",
    "\\t": "\t",
    "\\n": "\n",
    "\\f": "\f",
    "\\r": "\r",
    '\\"': '"',
    "\\\\": "\\",
}


class TOMLDecodeError(ValueError):
    """An error raised if a document is not valid TOML."""


def load(fp: Union[TextIO, BinaryIO]) -> Dict[str, Any]:
    """Parse TOML from a file path or file-like object.

    The file must be opened in binary mode and contain valid UTF-8 bytes.
    """
    try:
        s = fp.read()
    except AttributeError:
        raise TypeError("File must be a file-like object that is opened in binary mode")
    if isinstance(s, bytes):
        s = s.decode()
    return loads(s)


def loads(s: str) -> Dict[str, Any]:
    """Parse TOML from a string."""
    src = s.replace("\r\n", "\n")
    pos = 0
    out: Dict[str, Any] = {}
    header: Key = ()
    parse_float = float

    # Parse the document
    while pos < len(src):
        # Skip whitespace and comments
        pos = skip_whitespace_and_comments(src, pos)
        if pos >= len(src):
            break

        # Parse key-value pair or table header
        if src[pos] == "[":
            pos, header = parse_table_header(src, pos)
        else:
            pos, key, value = parse_key_value_pair(src, pos, parse_float)
            if header:
                nested_dict = out
                for k in header:
                    nested_dict = nested_dict.setdefault(k, {})
                nested_dict[key] = value
            else:
                out[key] = value

    return out


def skip_whitespace_and_comments(src: str, pos: Pos) -> Pos:
    """Skip whitespace and comments."""
    while pos < len(src):
        char = src[pos]
        if char in " \t":
            pos += 1
        elif char == "#":
            # Skip comment
            pos = src.find("\n", pos)
            if pos == -1:
                return len(src)
            pos += 1
        elif char in "\n\r":
            pos += 1
        else:
            break
    return pos


def parse_table_header(src: str, pos: Pos) -> tuple[Pos, Key]:
    """Parse table header like [table.name] or [[array.of.tables]]."""
    if src[pos] != "[":
        raise TOMLDecodeError(f"Expected '[' at position {pos}")
    pos += 1

    # Check for array of tables
    is_array_of_tables = pos < len(src) and src[pos] == "["
    if is_array_of_tables:
        pos += 1

    # Parse the key (potentially dotted)
    pos, key = parse_dotted_key(src, pos)

    # Expect closing bracket(s)
    if pos >= len(src) or src[pos] != "]":
        raise TOMLDecodeError(f"Expected ']' at position {pos}")
    pos += 1

    if is_array_of_tables:
        if pos >= len(src) or src[pos] != "]":
            raise TOMLDecodeError(f"Expected ']]' at position {pos}")
        pos += 1

    pos = skip_whitespace_and_comments(src, pos)
    return pos, key


def parse_key_value_pair(
    src: str, pos: Pos, parse_float: ParseFloat
) -> tuple[Pos, str, Any]:
    """Parse key = value pair."""
    pos, key = parse_key(src, pos)

    pos = skip_whitespace_and_comments(src, pos)
    if pos >= len(src) or src[pos] != "=":
        raise TOMLDecodeError(f"Expected '=' at position {pos}")
    pos += 1

    pos = skip_whitespace_and_comments(src, pos)
    pos, value = parse_value(src, pos, parse_float)

    return pos, key, value


def parse_key(src: str, pos: Pos) -> tuple[Pos, str]:
    """Parse a key (bare or quoted)."""
    pos = skip_whitespace_and_comments(src, pos)
    if pos >= len(src):
        raise TOMLDecodeError(f"Expected key at position {pos}")

    char = src[pos]
    if char == '"':
        return parse_basic_str(src, pos)
    elif char == "'":
        return parse_literal_str(src, pos)
    else:
        # Bare key
        start_pos = pos
        while pos < len(src) and src[pos] in BARE_KEY_CHARS:
            pos += 1
        if pos == start_pos:
            raise TOMLDecodeError(f"Expected key at position {pos}")
        return pos, src[start_pos:pos]


def parse_dotted_key(src: str, pos: Pos) -> tuple[Pos, Key]:
    """Parse a dotted key like 'table.name' or just 'name'."""
    key_parts: List[str] = []

    while True:
        pos, key_part = parse_key(src, pos)
        key_parts.append(key_part)

        pos = skip_whitespace_and_comments(src, pos)
        if pos >= len(src) or src[pos] != ".":
            break
        pos += 1  # Skip the dot
        pos = skip_whitespace_and_comments(src, pos)

    return pos, tuple(key_parts)


def parse_value(src: str, pos: Pos, parse_float: ParseFloat) -> tuple[Pos, Any]:
    """Parse a value."""
    pos = skip_whitespace_and_comments(src, pos)
    if pos >= len(src):
        raise TOMLDecodeError(f"Expected value at position {pos}")

    char = src[pos]
    if char == '"':
        if pos + 2 < len(src) and src[pos : pos + 3] == '"""':
            return parse_multiline_basic_str(src, pos)
        return parse_basic_str(src, pos)
    elif char == "'":
        if pos + 2 < len(src) and src[pos : pos + 3] == "'''":
            return parse_multiline_literal_str(src, pos)
        return parse_literal_str(src, pos)
    elif char == "[":
        return parse_array(src, pos, parse_float)
    elif char == "{":
        return parse_inline_table(src, pos, parse_float)
    elif char.lower() in "tf":
        return parse_bool(src, pos)
    elif char.isdigit() or char in "+-":
        return parse_number_or_datetime(src, pos, parse_float)
    else:
        raise TOMLDecodeError(f"Invalid value at position {pos}")


def parse_basic_str(src: str, pos: Pos) -> tuple[Pos, str]:
    """Parse a basic string."""
    if src[pos] != '"':
        raise TOMLDecodeError(f"Expected '\"' at position {pos}")
    pos += 1

    result: List[str] = []
    while pos < len(src):
        char = src[pos]
        if char == '"':
            pos += 1
            return pos, "".join(result)
        elif char == "\\":
            pos += 1
            if pos >= len(src):
                raise TOMLDecodeError(f"Unterminated string at position {pos}")
            escape_char = src[pos]
            if escape_char == "u":
                # Unicode escape
                pos += 1
                if pos + 4 > len(src):
                    raise TOMLDecodeError(f"Invalid unicode escape at position {pos}")
                hex_chars = src[pos : pos + 4]
                try:
                    code_point = int(hex_chars, 16)
                    result.append(chr(code_point))
                except ValueError:
                    raise TOMLDecodeError(f"Invalid unicode escape at position {pos}")
                pos += 4
            elif escape_char == "U":
                # Unicode escape (8 digits)
                pos += 1
                if pos + 8 > len(src):
                    raise TOMLDecodeError(f"Invalid unicode escape at position {pos}")
                hex_chars = src[pos : pos + 8]
                try:
                    code_point = int(hex_chars, 16)
                    result.append(chr(code_point))
                except ValueError:
                    raise TOMLDecodeError(f"Invalid unicode escape at position {pos}")
                pos += 8
            else:
                escape_seq = "\\" + escape_char
                if escape_seq in BASIC_STR_ESCAPE_REPLACEMENTS:
                    result.append(BASIC_STR_ESCAPE_REPLACEMENTS[escape_seq])
                else:
                    raise TOMLDecodeError(f"Invalid escape sequence at position {pos}")
                pos += 1
        elif char in ILLEGAL_BASIC_STR_CHARS:
            raise TOMLDecodeError(f"Illegal character in string at position {pos}")
        else:
            result.append(char)
            pos += 1

    raise TOMLDecodeError(f"Unterminated string at position {pos}")


def parse_literal_str(src: str, pos: Pos) -> tuple[Pos, str]:
    """Parse a literal string."""
    if src[pos] != "'":
        raise TOMLDecodeError(f'Expected "\'" at position {pos}')
    pos += 1

    start_pos = pos
    while pos < len(src) and src[pos] != "'":
        if src[pos] in ASCII_CTRL and src[pos] != "\t":
            raise TOMLDecodeError(
                f"Illegal character in literal string at position {pos}"
            )
        pos += 1

    if pos >= len(src):
        raise TOMLDecodeError(f"Unterminated literal string at position {pos}")

    result = src[start_pos:pos]
    pos += 1
    return pos, result


def parse_multiline_basic_str(src: str, pos: Pos) -> tuple[Pos, str]:
    """Parse a multiline basic string."""
    if src[pos : pos + 3] != '"""':
        raise TOMLDecodeError(f'Expected \'"""\' at position {pos}')
    pos += 3

    # Skip initial newline
    if pos < len(src) and src[pos] == "\n":
        pos += 1

    result: List[str] = []
    while pos < len(src):
        if src[pos : pos + 3] == '"""':
            pos += 3
            return pos, "".join(result)
        elif src[pos] == "\\":
            pos += 1
            if pos >= len(src):
                raise TOMLDecodeError(f"Unterminated string at position {pos}")

            # Handle line ending backslash
            if src[pos] == "\n":
                pos += 1
                # Skip whitespace after line ending backslash
                while pos < len(src) and src[pos] in " \t\n":
                    pos += 1
                continue

            escape_char = src[pos]
            if escape_char == "u":
                # Unicode escape
                pos += 1
                if pos + 4 > len(src):
                    raise TOMLDecodeError(f"Invalid unicode escape at position {pos}")
                hex_chars = src[pos : pos + 4]
                try:
                    code_point = int(hex_chars, 16)
                    result.append(chr(code_point))
                except ValueError:
                    raise TOMLDecodeError(f"Invalid unicode escape at position {pos}")
                pos += 4
            elif escape_char == "U":
                # Unicode escape (8 digits)
                pos += 1
                if pos + 8 > len(src):
                    raise TOMLDecodeError(f"Invalid unicode escape at position {pos}")
                hex_chars = src[pos : pos + 8]
                try:
                    code_point = int(hex_chars, 16)
                    result.append(chr(code_point))
                except ValueError:
                    raise TOMLDecodeError(f"Invalid unicode escape at position {pos}")
                pos += 8
            else:
                escape_seq = "\\" + escape_char
                if escape_seq in BASIC_STR_ESCAPE_REPLACEMENTS:
                    result.append(BASIC_STR_ESCAPE_REPLACEMENTS[escape_seq])
                else:
                    raise TOMLDecodeError(f"Invalid escape sequence at position {pos}")
                pos += 1
        else:
            result.append(src[pos])
            pos += 1

    raise TOMLDecodeError(f"Unterminated multiline string at position {pos}")


def parse_multiline_literal_str(src: str, pos: Pos) -> tuple[Pos, str]:
    """Parse a multiline literal string."""
    if src[pos : pos + 3] != "'''":
        raise TOMLDecodeError(f"Expected \"'''\" at position {pos}")
    pos += 3

    # Skip initial newline
    if pos < len(src) and src[pos] == "\n":
        pos += 1

    start_pos = pos
    while pos < len(src):
        if src[pos : pos + 3] == "'''":
            result = src[start_pos:pos]
            pos += 3
            return pos, result
        pos += 1

    raise TOMLDecodeError(f"Unterminated multiline literal string at position {pos}")


def parse_array(src: str, pos: Pos, parse_float: ParseFloat) -> tuple[Pos, List[Any]]:
    """Parse an array."""
    if src[pos] != "[":
        raise TOMLDecodeError(f"Expected '[' at position {pos}")
    pos += 1

    result: List[Any] = []
    pos = skip_whitespace_and_comments(src, pos)

    if pos < len(src) and src[pos] == "]":
        pos += 1
        return pos, result

    while pos < len(src):
        pos, value = parse_value(src, pos, parse_float)
        result.append(value)

        pos = skip_whitespace_and_comments(src, pos)
        if pos >= len(src):
            raise TOMLDecodeError(f"Unterminated array at position {pos}")

        if src[pos] == "]":
            pos += 1
            return pos, result
        elif src[pos] == ",":
            pos += 1
            pos = skip_whitespace_and_comments(src, pos)
            if pos < len(src) and src[pos] == "]":
                pos += 1
                return pos, result
        else:
            raise TOMLDecodeError(f"Expected ',' or ']' at position {pos}")

    raise TOMLDecodeError(f"Unterminated array at position {pos}")


def parse_inline_table(
    src: str, pos: Pos, parse_float: ParseFloat
) -> tuple[Pos, Dict[str, Any]]:
    """Parse an inline table."""
    if src[pos] != "{":
        raise TOMLDecodeError(f"Expected '{{' at position {pos}")
    pos += 1

    result: Dict[str, Any] = {}
    pos = skip_whitespace_and_comments(src, pos)

    if pos < len(src) and src[pos] == "}":
        pos += 1
        return pos, result

    while pos < len(src):
        pos, key, value = parse_key_value_pair(src, pos, parse_float)
        result[key] = value

        pos = skip_whitespace_and_comments(src, pos)
        if pos >= len(src):
            raise TOMLDecodeError(f"Unterminated inline table at position {pos}")

        if src[pos] == "}":
            pos += 1
            return pos, result
        elif src[pos] == ",":
            pos += 1
            pos = skip_whitespace_and_comments(src, pos)
        else:
            raise TOMLDecodeError(f"Expected ',' or '}}' at position {pos}")

    raise TOMLDecodeError(f"Unterminated inline table at position {pos}")


def parse_bool(src: str, pos: Pos) -> tuple[Pos, bool]:
    """Parse a boolean value."""
    if src[pos : pos + 4] == "true":
        return pos + 4, True
    elif src[pos : pos + 5] == "false":
        return pos + 5, False
    else:
        raise TOMLDecodeError(f"Invalid boolean at position {pos}")


def parse_number_or_datetime(
    src: str, pos: Pos, parse_float: ParseFloat
) -> tuple[Pos, Any]:
    """Parse a number or datetime."""
    # First try to match datetime
    datetime_match = RE_DATETIME.match(src, pos)
    if datetime_match:
        return pos + len(datetime_match.group()), match_to_datetime(datetime_match)

    # Try to match local time
    localtime_match = RE_LOCALTIME.match(src, pos)
    if localtime_match:
        return pos + len(localtime_match.group()), match_to_localtime(localtime_match)

    # Try to match number
    number_match = RE_NUMBER.match(src, pos)
    if number_match:
        return pos + len(number_match.group()), match_to_number(
            number_match, parse_float
        )

    raise TOMLDecodeError(f"Invalid number or datetime at position {pos}")
