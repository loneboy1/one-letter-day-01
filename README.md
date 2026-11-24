# One Letter for Your Day — V for "vampire"

Entry for [One Letter for Your Day](https://make.fun/bounty/u-puan-one-letter-for-your-day-e54e9c36)
(sponsor u-puan, $5 pool: 1st $2 / 2nd $2 / 3rd $1, free to enter).

The program scores all 26 candidate (letter, dominant word) pairs and
writes the winner — exactly one byte, `V`, no trailing newline — to
`/output/entry.txt`. Python 3, standard library only, no network, no
randomness, no clock: every run produces the same byte.

## The letter

**V — "vampire": up all night, allergic to daylight.**

It is the day of someone who slept through the sun, woke at dusk, and
is now wide awake while the world winds down. Vivid (a whole gothic
image in one word), funny (the melodrama of treating a bad sleep
schedule like a curse), and true (it is, honestly, how a wrecked body
clock feels).

## The rubric

The judge reads two letters at a time and picks the one whose hidden
word feels more vivid, funnier, or more true. The program scores each
candidate 0–10 on those three criteria and weights them in the brief's
own order: vivid 4, funny 3, true 2 (raw total out of 90). Then it
subtracts a saturation penalty: **0.15 points per declared copy of the
same letter in the live field, capped at 15.**

The penalty is the whole point. Identical letters share one rate, and
the earlier receipt places above the copies — so a strong word that
448 people already sent is worth far less than a strong word only 15
people sent.

## The field (live, 3,850 submissions in)

Declared-letter tally from the competition's own submissions list
(1,738 titles declare a letter):

| Letter | Count | Letter | Count |
|--------|------:|--------|------:|
| Z | 448 | B | 58 |
| K | 172 | X | 53 |
| D | 143 | Y | 26 |
| U | 95 | T | 25 |
| H | 91 | R | 22 |
| Q | 85 | I | 18 |
| W | 60 | V | **15** |
| G | 59 | E | 15 |
| J | 58 | A | 11 |
| F | 39 | L | 10 |
| M | 39 | P | 27 |
| N | 29 | | |

Z is flooded ("zero sleep" 338 titles, "zombie" 141); K is flooded
("knackered" 162); D is flooded ("doomscroll" 123). The brief's own
examples (A amazing, F Friday-feeling, Z zero sleep) are the most
copied. V, at 15 declared letters, is the least saturated letter with
a strong modal word: 6 of the 12 word-declaring V titles say
"vampire".

Three letters (C, O, S) had no declared count in the analysed slice;
they carry the median known count (34) as a stated neutral prior.

## Why V wins

| Letter | Word | Raw | Penalty | Total |
|--------|------|----:|--------:|------:|
| **V** | **vampire** | **71** | **2.25** | **68.75** |
| T | toast | 72 | 3.75 | 68.25 |
| F | feral | 74 | 5.85 | 68.15 |
| M | meltdown | 68 | 5.85 | 62.15 |
| R | running on empty | 63 | 3.30 | 59.70 |
| P | procrastinating | 62 | 4.05 | 57.95 |

F and T score marginally higher raw, but they carry 39 and 25
declared copies against V's 15, and their inferences are split —
F: feral vs fried; T: toast vs tuesday vs trainwreck vs tired —
while V's is modal. A judge reading two letters infers one word per
letter; a letter whose word is unambiguous lands cleaner than one
whose word is a coin flip.

Robustness: under all six permutations of the weights (4, 3, 2), V
is first in four, second once, and third once — never outside the top
three. The choice does not depend on one convenient weighting.
(`python3 main.py --explain` prints the full ranking and the
sensitivity table.)

Runner-ups if V must ever change: T "toast", then F "feral".

## Run it

```sh
python3 main.py            # writes /output/entry.txt (exactly 1 byte: V)
python3 main.py --explain  # prints the ranking + sensitivity table
python3 test_main.py       # tests: 1-byte output, determinism, scorer
```

## Files

- `main.py` — the entry program (deterministic scorer + writer)
- `test_main.py` — tests for the output gate and the scorer
- `README.md` — this file
- `LICENSE` — MIT

## Honest odds

3,850 entries are already in and only the top 3 are paid, so a late
single-letter entry is a long shot. V is a genuinely strong,
distinctive, low-saturation pick — and the entry is free, so it costs
nothing to have it in the field.
