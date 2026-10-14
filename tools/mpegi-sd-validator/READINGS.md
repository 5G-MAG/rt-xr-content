# Independent readings of the rules

Each rule of `rules.json` that rests on ISO/IEC 23090-14:2024(E) was read a second time by a reader who was shown the code that
raises it and the text of the clause, and nothing else: not the rule's title, its quotation, its tests or this repository's README.
The 46 rules read are those with a clause in the text; the schema pass-through, the two glTF integrity rules and the empty-range
warning (`MEDIA-004`, no clause governs it) are not covered.

Where the reading differed from the rule, or could not judge, a third reader, who did not know which of the two earlier readings was
which, read it again with the helper code and tables the first reader lacked. The verdict two readings agree on stands.

| Rule | First reading | Third reading | Outcome |
|---|---|---|---|
| ACC-001 | stricter: the text states the converse | cannot judge, no sentence found | removed (no sentence states it) |
| TEX-004 | stricter: 5.3.1.3 allows the decoder's own picture size | stricter | removed |
| EXT-002 | stricter: the text does not forbid other MPEG_ names | stricter | error became warning |
| BUF-004 | stricter: the text does not define the frame size | stricter | error became warning |
| EXT-003 | cannot judge (table not shown) | implemented | unchanged |
| AUD-001 | weaker ('source' in the sentence, 'sources' in Table 13) | implemented | unchanged; note added |
| AUD-002 | differs ('reverb' in the sentence, 'reverbs' in Table 13) | cannot judge | unchanged; text inconsistent, both accepted, note added |
| ACC-006 | weaker (plain accessors not counted) | implemented | unchanged; they are reported by ACC-005 |
| INT-001 | cannot judge (table not shown) | implemented | unchanged; basis is a reference between indices |
| MEDIA-002 | weaker (only booleans) | implemented | unchanged; the JSON schema rejects the other types |

The other 36 rules were read as matching the text. These are readings by language-model readers and have not been checked against an
independent implementation.
