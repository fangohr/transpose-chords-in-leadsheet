from __future__ import annotations

from dataclasses import dataclass
import re

SHARP_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NOTES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

NOTE_TO_INDEX = {
    "C": 0,
    "B#": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "Fb": 4,
    "F": 5,
    "E#": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
    "Cb": 11,
}

GERMAN_B_ALIASES = {"H": "B", "h": "B"}

CHORD_BODY_PART = re.compile(
    r"(maj|min|dim|aug|sus|add|omit|no|dom|alt|M|m|Δ|ø|°|\+|-|#|b|\d+|\(|\))"
)
CHORD_RE = re.compile(
    r"^(?P<root>(?:[A-G](?:#|b)?|[Hh]))"
    r"(?P<body>(?:(?:maj|min|dim|aug|sus|add|omit|no|dom|alt|M|m|Δ|ø|°|\+|-|#|b|\d+|\(|\))*)?)"
    r"(?P<slash>/(?P<bass>(?:[A-G](?:#|b)?|[Hh])))?$"
)
LINE_SPLIT_RE = re.compile(r"(\r\n|\r|\n)")
TOKEN_SPLIT_RE = re.compile(r"([^\S\r\n]+)")
ROOT_PREFIX_RE = re.compile(r"^(?:[A-G](?:#|b)?|[Hh])")


class ChordParseError(ValueError):
    """Raised when text appears to be chord notation but cannot be parsed safely."""

    pass


@dataclass(frozen=True)
class ParsedChord:
    """Normalized representation of one chord symbol before transposition."""

    root: str
    body: str
    bass: str | None = None


@dataclass(frozen=True)
class ClassifiedLine:
    """Line classification result carrying the rendered content and explanation."""

    kind: str
    content: str
    reason: str


def transpose_chord_symbol(
    chord: str, semitones: int, prefer_flats: bool = False
) -> str:
    """Transpose one chord symbol while preserving its chord quality text."""
    parsed = parse_chord_symbol(chord)
    transposed_root = transpose_note(parsed.root, semitones, prefer_flats=prefer_flats)
    if parsed.bass is None:
        return f"{transposed_root}{parsed.body}"

    transposed_bass = transpose_note(parsed.bass, semitones, prefer_flats=prefer_flats)
    return f"{transposed_root}{parsed.body}/{transposed_bass}"


def transpose_note(note: str, semitones: int, prefer_flats: bool = False) -> str:
    """Transpose a note name by semitones and render it in the configured style."""
    try:
        index = NOTE_TO_INDEX[note]
    except KeyError as exc:
        raise ChordParseError(f"Unsupported note name: {note}") from exc

    notes = FLAT_NOTES if prefer_flats else SHARP_NOTES
    return notes[(index + semitones) % 12]


def parse_chord_symbol(token: str) -> ParsedChord:
    """Parse a single chord token into normalized root, body, and optional bass."""
    match = CHORD_RE.fullmatch(token)
    if not match:
        raise ChordParseError(f"Unable to parse chord symbol: {token}")

    body = match.group("body") or ""
    if body and not _body_is_valid(body):
        raise ChordParseError(f"Unable to parse chord symbol: {token}")

    return ParsedChord(
        root=_normalize_note_alias(match.group("root")),
        body=body,
        bass=_normalize_note_alias(match.group("bass")),
    )


def transpose_token(token: str, semitones: int, prefer_flats: bool = False) -> str:
    """Transpose a token, rejecting malformed tokens that look chord-like."""
    if is_chord_symbol(token):
        return transpose_chord_symbol(token, semitones, prefer_flats=prefer_flats)
    if looks_like_chord(token):
        raise ChordParseError(
            f"Unable to parse chord-like token '{token}'. "
            "Please fix the notation in the input file and run the tool again."
        )
    return token


def transpose_text(text: str, semitones: int, prefer_flats: bool = False) -> str:
    """Transpose chord lines in a text block while preserving line endings."""
    parts = LINE_SPLIT_RE.split(text)
    transposed_parts = []
    for part in parts:
        if LINE_SPLIT_RE.fullmatch(part):
            transposed_parts.append(part)
            continue
        transposed_parts.append(
            transpose_line(part, semitones=semitones, prefer_flats=prefer_flats)
        )
    return "".join(transposed_parts)


def debug_text(text: str, semitones: int, prefer_flats: bool = False) -> str:
    """Return transposed text with each line prefixed by its classification."""
    parts = LINE_SPLIT_RE.split(text)
    classified_lines: list[tuple[ClassifiedLine, str]] = []
    labels = []
    for index in range(0, len(parts), 2):
        line = parts[index]
        newline = parts[index + 1] if index + 1 < len(parts) else ""
        if line == "" and newline == "":
            continue
        classified = classify_line(line, semitones=semitones, prefer_flats=prefer_flats)
        label = f"{classified.kind} ({classified.reason}): "
        labels.append(label)
        classified_lines.append((classified, newline))

    content_start = max((len(label) for label in labels), default=0)
    debug_parts = []
    for (classified, newline), label in zip(classified_lines, labels, strict=True):
        padding = " " * (content_start - len(label))
        debug_parts.append(f"{label}{padding}{classified.content}{newline}")
    return "".join(debug_parts)


def transpose_line(line: str, semitones: int, prefer_flats: bool = False) -> str:
    """Transpose one line if it is classified as a chord line."""
    return classify_line(line, semitones=semitones, prefer_flats=prefer_flats).content


def classify_line(line: str, semitones: int, prefer_flats: bool = False) -> ClassifiedLine:
    """Classify one line as chords or text and transpose chord lines only."""
    parts = TOKEN_SPLIT_RE.split(line)
    tokens = [part for part in parts if part and not part.isspace()]
    chord_decision = _classify_tokens(tokens)
    if chord_decision.kind == "text":
        return ClassifiedLine(kind="text", content=line, reason=chord_decision.reason)

    transposed_parts = []
    for part in parts:
        if not part or part.isspace():
            transposed_parts.append(part)
            continue
        transposed_parts.append(
            transpose_token(part, semitones=semitones, prefer_flats=prefer_flats)
        )
    return ClassifiedLine(
        kind="chords",
        content="".join(transposed_parts),
        reason=chord_decision.reason,
    )


def is_chord_symbol(token: str) -> bool:
    """Return whether a token can be parsed as a supported chord symbol."""
    try:
        parse_chord_symbol(token)
    except ChordParseError:
        return False
    return True


def looks_like_chord(token: str) -> bool:
    """Return whether a token has enough chord syntax to flag bad notation."""
    prefix = ROOT_PREFIX_RE.match(token)
    if prefix is None:
        return False

    remainder = token[prefix.end() :]
    if not remainder:
        return True

    saw_strong_chord_marker = False
    position = 0
    while position < len(remainder):
        if remainder[position] == "/":
            return True

        match = CHORD_BODY_PART.match(remainder, position)
        if match is None:
            return saw_strong_chord_marker
        if _is_strong_chord_marker(match.group(0)):
            saw_strong_chord_marker = True
        position = match.end()

    return True


def _classify_tokens(tokens: list[str]) -> ClassifiedLine:
    """Decide whether a sequence of non-space tokens should be treated as chords."""
    if not tokens:
        return ClassifiedLine(
            kind="text",
            content="",
            reason="empty line",
        )

    valid_chord_count = 0
    chord_like_count = 0
    for token in tokens:
        if is_chord_symbol(token):
            valid_chord_count += 1
            continue
        if looks_like_chord(token):
            chord_like_count += 1
            continue
        return ClassifiedLine(
            kind="text",
            content="",
            reason=f"contains non-chord token {token!r}",
        )

    if valid_chord_count == len(tokens):
        token_word = "token" if valid_chord_count == 1 else "tokens"
        return ClassifiedLine(
            kind="chords",
            content="",
            reason=f"all {valid_chord_count} {token_word} parsed as chords",
        )

    if valid_chord_count >= 2:
        chord_word = "token" if valid_chord_count == 1 else "tokens"
        chord_like_word = "token" if chord_like_count == 1 else "tokens"
        return ClassifiedLine(
            kind="chords",
            content="",
            reason=(
                f"identified {valid_chord_count} chord {chord_word}; "
                f"{chord_like_count} additional {chord_like_word} looked chord-like"
            ),
        )

    return ClassifiedLine(
        kind="text",
        content="",
        reason=(
            f"only {valid_chord_count} valid chord token found; "
            f"need at least 2 before trusting chord-like tokens"
        ),
    )


def _body_is_valid(body: str) -> bool:
    """Validate that a chord body consists only of known body fragments."""
    position = 0
    while position < len(body):
        match = CHORD_BODY_PART.match(body, position)
        if match is None:
            return False
        position = match.end()
    return True


def _is_strong_chord_marker(marker: str) -> bool:
    """Return whether a body fragment strongly indicates chord notation."""
    return marker != "-"


def _normalize_note_alias(note: str | None) -> str | None:
    """Map accepted note aliases to their canonical internal note names."""
    if note is None:
        return None
    return GERMAN_B_ALIASES.get(note, note)
