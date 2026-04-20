# chord-transpose

Transpose whitespace-delimited chord symbols in mixed chord/lyric text while preserving the original whitespace layout.

Example:

```bash
transpose-chords inputfile.txt +3 outputfile.txt
```


## For developers

Short example for transposing individual chords.

```python
from chord_transpose import transpose_chord_symbol

print(transpose_chord_symbol("C", 2))
```

This prints `D`.

## Tool usage

Created with Codex (GPT-5.4).
