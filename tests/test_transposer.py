from pathlib import Path

import pytest

from chord_transpose import ChordParseError, transpose_chord_symbol, transpose_text
from chord_transpose.cli import main


@pytest.mark.parametrize(
    ("chord", "shift", "expected"),
    [
        ("C", 2, "D"),
        ("F#", 3, "A"),
        ("Gb", -1, "F"),
        ("B", 1, "C"),
        ("A", 12, "A"),
        ("D", -12, "D"),
        ("D", -14, "C"),
        ("Bbmaj7", 2, "Cmaj7"),
        ("C/E", 2, "D/F#"),
        ("G#m7b5", -2, "F#m7b5"),
    ],
)
def test_transpose_chord_symbol_examples(chord: str, shift: int, expected: str) -> None:
    assert transpose_chord_symbol(chord, shift) == expected


def test_prefer_flats_output() -> None:
    assert transpose_chord_symbol("F#", 3, prefer_flats=True) == "A"
    assert transpose_chord_symbol("C#", 2, prefer_flats=True) == "Eb"


def test_preserves_whitespace_layout_in_mixed_text() -> None:
    text = "C   G/B\nhello   world\nF#sus4   text\n"
    expected = "D   A/C#\nhello   world\nG#sus4   text\n"
    assert transpose_text(text, 2) == expected


def test_invalid_chord_like_token_raises() -> None:
    with pytest.raises(ChordParseError):
        transpose_text("Cmaj7x lyrics", 1)


def test_words_starting_with_note_letters_are_left_unchanged() -> None:
    text = "Das Es Am Ende\n"
    assert transpose_text(text, 2) == "Das Es Bm Ende\n"


@pytest.mark.parametrize(
    "chord",
    [
        "C",
        "C#",
        "Db",
        "D",
        "D#",
        "Eb",
        "E",
        "F",
        "F#",
        "Gb",
        "G",
        "G#",
        "Ab",
        "A",
        "A#",
        "Bb",
        "B",
    ],
)
def test_transposing_by_plus_or_minus_twelve_returns_original_pitch(chord: str) -> None:
    normalized = transpose_chord_symbol(chord, 0)
    assert transpose_chord_symbol(chord, 12) == normalized
    assert transpose_chord_symbol(chord, -12) == normalized


@pytest.mark.parametrize(
    ("song_path", "expected_plus_two_snippet", "expected_minus_two_snippet"),
    [
        (
            "songs/house-of-the-rising-sun.txt",
            "Bm     D      E       G",
            "Gm     A#      C       D#",
        ),
        (
            "songs/scarborough-fair.txt",
            "Bm        A        Bm",
            "Gm        F        Gm",
        ),
    ],
)
def test_song_examples_transpose_plus_and_minus_two(
    song_path: str,
    expected_plus_two_snippet: str,
    expected_minus_two_snippet: str,
) -> None:
    original = Path(song_path).read_text(encoding="utf-8")

    transposed_up = transpose_text(original, 2)
    transposed_down = transpose_text(original, -2)

    assert expected_plus_two_snippet in transposed_up
    assert expected_minus_two_snippet in transposed_down
    assert transpose_text(transposed_up, -2) == original
    assert transpose_text(transposed_down, 2) == original


def test_cli_prints_to_stdout_when_outputfile_is_omitted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    inputfile = tmp_path / "input.txt"
    inputfile.write_text("C   G/B\nlyrics line\n", encoding="utf-8")

    exit_code = main([str(inputfile), "+2"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "D   A/C#\nlyrics line\n"
    assert captured.err == ""


def test_cli_writes_outputfile_when_provided(tmp_path: Path) -> None:
    inputfile = tmp_path / "input.txt"
    outputfile = tmp_path / "output.txt"
    inputfile.write_text("C Em Am F\n", encoding="utf-8")

    exit_code = main([str(inputfile), "-2", str(outputfile)])

    assert exit_code == 0
    assert outputfile.read_text(encoding="utf-8") == "A# Dm Gm D#\n"
