# chord-transpose

Transpose whitespace-delimited chord symbols in mixed chord/lyric text while preserving the original whitespace layout.

Example:

```bash
transpose-chords inputfile.txt +3 outputfile.txt
```


# For developers

## Tool usage

Created with Codex (GPT-5.4).

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



