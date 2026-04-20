# chord-transpose

Transpose whitespace-delimited chord symbols in mixed chord/lyric text while preserving the original whitespace layout.

The examples below work on this text-based leadsheet with lyrics and chords (`songs/scarborough-fair.txt`):

```
Am        G        Am
Are you going to Scarborough Fair?
C            G        Am
Parsley, sage, rosemary and thyme
Am            G           Am
Remember me to one who lives there
C         G        Am
She once was a true love of mine
```

## Transpose song up by one tone (=two semitones)

We can transpose by any number of semitones. For example 2 semitones up (`+2`):

```bash
transpose-chords songs/scarborough-fair.txt +2
Bm        A        Bm
Are you going to Scarborough Fair?
D            A        Bm
Parsley, sage, rosemary and thyme
Bm            A           Bm
Remember me to one who lives there
D         A        Bm
She once was a true love of mine
```

### Sharp or flats?

By default, we use sharps (`#`) but can switch to flats (`b`) if preferred. Example (default sharps):

```bash
transpose-chords songs/scarborough-fair.txt +3
Cm        A#        Cm
Are you going to Scarborough Fair?
D#            A#        Cm
Parsley, sage, rosemary and thyme
Cm            A#           Cm
Remember me to one who lives there
D#         A#        Cm
She once was a true love of mine
```

Flats if desired (`--prefer-flats`):
```bash
transpose-chords songs/scarborough-fair.txt +3 --prefer-flats
Cm        Bb        Cm
Are you going to Scarborough Fair?
Eb            Bb        Cm
Parsley, sage, rosemary and thyme
Cm            Bb           Cm
Remember me to one who lives there
Eb         Bb        Cm
She once was a true love of mine
```

# For developers

## Tool usage

Created with Codex (GPT-5.4)

## Single Chord/tone transpose

Short example for transposing individual chords.

```python
from chord_transpose import transpose_chord_symbol

print(transpose_chord_symbol("C", 2))
```

This prints `D`.

If this is of interested, you probably want to use `pychord` (see below).

## Related python packages

- [chordstransposer on PyPI](https://pypi.org/project/chordstransposer/)
- [pychord on PyPI](https://pypi.org/project/pychord/)
- [pytransposer on PyPI](https://pypi.org/project/pytransposer/)
- [chordparser on PyPI](https://pypi.org/project/chordparser/)

My read:
- `pychord` is a parser/transposition core which could be used in this
  project as a depedency. Looks powerful (more than we need here).
- `chordstransposer` is close match to the functionality of this
  tool. Available on PyPI but github source
  (https://github.com/benterris/chords-transposer) seems tohave
  disappeared.

Unique features of this package:

- narrow focus: whitespace-preserving file CLI
- explicit error behavior for chord-like tokens
- pixi-based workflow
- tests around your exact song-sheet format.



