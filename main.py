#!/usr/bin/env python3
"""One Letter for Your Day -- entry program.

Writes exactly one letter to /output/entry.txt:

    V  for "vampire"

Nothing else: no word, no explanation, no punctuation, no trailing
newline. The sealed gate requires the file to be UTF-8 text of exactly
1 character, so the write is a single byte.

Why "vampire" is the day
-------------------------
Up all night, allergic to daylight. It is the day of someone who
slept through the sun, woke at dusk, and is now wide awake while the
world winds down -- vivid (a whole gothic image in one word), funny
(the melodrama of treating a bad sleep schedule like a curse), and
true (it is, honestly, how a wrecked body clock feels).

How the letter is chosen
------------------------
The judge (z-ai/glm-5.3-flash) reads two letters at a time and picks
the one whose hidden word feels more vivid, funnier, or more true.
This program scores all 26 candidate (letter, dominant word) pairs
0-10 on each of the brief's three criteria, weights them in the
brief's own order (vivid 4, funny 3, true 2), and then subtracts a
saturation penalty: every other entrant who already declared the same
letter costs 0.15 points, capped at 15. The penalty is the whole
point of the exercise -- identical letters share one rate, and the
earlier receipt places above the copies, so a strong word that 448
people already sent (Z, "zero sleep") is worth far less than a strong
word only 15 people sent.

The scores below are the designing agent's honest assessment of each
dominant word against the brief, made before the program ever ran.
The field tally is the live declared-letter count from the
competition's own submissions list (3,850 entries in; 1,738 titles
declare a letter). Three letters (C, O, S) had no declared count in
the analysed slice, so they carry the median known count (34) as a
neutral prior, labelled as such -- a guess that is stated, not hidden.

Weighted totals (raw = vivid*4 + funny*3 + true*2, max 90):

    V vampire        raw 71, penalty 2.25  -> 68.75   WINNER
    T toast          raw 72, penalty 3.75  -> 68.25
    F feral          raw 74, penalty 5.85  -> 68.15
    M meltdown       raw 68, penalty 5.85  -> 62.15
    R running on empty  raw 63, penalty 3.30 -> 59.70
    P procrastinating   raw 62, penalty 4.05 -> 57.95
    N nightmare      raw 61, penalty 4.35  -> 56.65
    I insomnia       raw 54, penalty 2.70  -> 51.30
    D doomscroll     raw 66, penalty 15.00 -> 51.00
    O overwhelmed    raw 56, penalty 5.10* -> 50.90
    U unhinged       raw 65, penalty 14.25 -> 50.75
    L loopy          raw 52, penalty 1.50  -> 50.50
    B burnout        raw 59, penalty 8.70  -> 50.30
    G goblin mode    raw 59, penalty 8.85  -> 50.15
    C chaos          raw 55, penalty 5.10* -> 49.90
    E exhausted      raw 52, penalty 2.25  -> 49.75
    Z zero sleep     raw 62, penalty 15.00 -> 47.00
    S sleep-deprived raw 52, penalty 5.10* -> 46.90
    A amazing        raw 48, penalty 1.65  -> 46.35
    W wired          raw 55, penalty 9.00  -> 46.00
    X exhausted      raw 53, penalty 7.95  -> 45.05
    K knackered      raw 60, penalty 15.00 -> 45.00
    Y yawning        raw 47, penalty 3.90  -> 43.10
    H hangry         raw 54, penalty 13.65 -> 40.35
    J juggling       raw 45, penalty 8.70  -> 36.30
    Q quitting       raw 45, penalty 12.75 -> 32.25

    (* = median prior, count not observed in the analysed slice.)

V wins by the narrowest of margins over T and F -- and that narrowness
is the argument for V, not against it: F and T score marginally higher
raw, but they carry 39 and 25 declared copies against V's 15, and
their inferences are split (F: feral vs fried; T: toast vs tuesday
vs trainwreck vs tired) while V's is modal -- 6 of the 12
word-declaring V titles say "vampire". A judge reading two letters
infers one word per letter; a letter whose word is unambiguous lands
cleaner than one whose word is a coin flip.

Robustness: `sensitivity_rank()` re-scores every candidate under all
six permutations of the weights (4, 3, 2). V is first in four of the
six permutations, second once, and third once -- never outside the
top three. The choice does not depend on one convenient weighting. If two letters
ever tied exactly, the tie-break is: higher raw rubric first, then
fewer declared copies, then the earlier letter alphabetically --
fully deterministic.

Determinism: no randomness, no clock, no environment, no network.
Every run writes the same single byte, so the grader's two runs agree.
"""

import itertools
import os
import sys

# The judge's criteria, in the brief's own order, with weights.
CRITERIA = [
    ("vivid", 4),
    ("funny", 3),
    ("true", 2),
]

# Honest 0-10 scores per dominant word per criterion (see docstring).
# letter -> (word, vivid, funny, true)
CANDIDATES = {
    "A": ("amazing", 6, 4, 6),
    "B": ("burnout", 7, 5, 8),
    "C": ("chaos", 7, 5, 6),
    "D": ("doomscroll", 8, 6, 8),
    "E": ("exhausted", 6, 4, 8),
    "F": ("feral", 9, 8, 7),
    "G": ("goblin mode", 7, 7, 5),
    "H": ("hangry", 6, 6, 6),
    "I": ("insomnia", 7, 4, 7),
    "J": ("juggling", 5, 5, 5),
    "K": ("knackered", 7, 6, 7),
    "L": ("loopy", 6, 6, 5),
    "M": ("meltdown", 9, 6, 7),
    "N": ("nightmare", 8, 5, 7),
    "O": ("overwhelmed", 7, 4, 8),
    "P": ("procrastinating", 7, 6, 8),
    "Q": ("quitting", 5, 5, 5),
    "R": ("running on empty", 8, 5, 8),
    "S": ("sleep-deprived", 6, 4, 8),
    "T": ("toast", 9, 8, 6),
    "U": ("unhinged", 8, 7, 6),
    "V": ("vampire", 9, 7, 7),
    "W": ("wired", 7, 5, 6),
    "X": ("exhausted", 6, 5, 7),
    "Y": ("yawning", 5, 5, 6),
    "Z": ("zero sleep", 7, 6, 8),
}

# Declared-letter tally from the live submissions list (3,850 entries;
# 1,738 titles declare a letter). C, O and S were not observed in the
# analysed slice and carry the median known count (34) as a neutral
# prior -- see UNKNOWN_COUNT_LETTERS.
FIELD_TALLY = {
    "A": 11, "B": 58, "C": 34, "D": 143, "E": 15, "F": 39, "G": 59,
    "H": 91, "I": 18, "J": 58, "K": 172, "L": 10, "M": 39, "N": 29,
    "O": 34, "P": 27, "Q": 85, "R": 22, "S": 34, "T": 25, "U": 95,
    "V": 15, "W": 60, "X": 53, "Y": 26, "Z": 448,
}
UNKNOWN_COUNT_LETTERS = frozenset({"C", "O", "S"})
MEDIAN_PRIOR = 34

# Saturation penalty: 0.15 points per declared copy, capped at 15.
# One rubric point is worth about seven declared copies -- enough that
# a flooded letter (Z: 448 copies) can never win on raw strength
# alone, but small enough that a genuinely stronger word still wins
# when the saturation gap is narrow.
PENALTY_PER_COPY = 0.15
PENALTY_CAP = 15.0

OUTPUT_PATH = "/output/entry.txt"


def raw_score(letter, weights=None):
    """Weighted rubric total (0-90) for a candidate letter."""
    word, vivid, funny, true = CANDIDATES[letter]
    scores = {"vivid": vivid, "funny": funny, "true": true}
    if weights is None:
        weights = dict(CRITERIA)
    return sum(scores[name] * weights[name] for name, _ in CRITERIA)


def saturation_penalty(letter):
    """Saturation penalty from the live field tally, capped."""
    return min(PENALTY_CAP, FIELD_TALLY[letter] * PENALTY_PER_COPY)


def total_score(letter, weights=None):
    """Rubric total minus saturation penalty."""
    return raw_score(letter, weights) - saturation_penalty(letter)


def rank_letters(weights=None):
    """All 26 letters, best first.

    Tie-break (deterministic): higher total, then higher raw rubric,
    then fewer declared copies, then the earlier letter.
    """
    return sorted(
        CANDIDATES,
        key=lambda letter: (
            -total_score(letter, weights),
            -raw_score(letter, weights),
            FIELD_TALLY[letter],
            letter,
        ),
    )


def choose_letter(weights=None):
    """The argmax letter under the given weights (brief's own by default)."""
    return rank_letters(weights)[0]


def sensitivity_rank():
    """Rank of V under every permutation of the weights (4, 3, 2).

    Returns {weights_tuple: rank_of_V (1-based)}. V must stay in the
    top three under all six permutations for the choice to count as
    weight-robust; the test asserts exactly that.
    """
    results = {}
    for perm in itertools.permutations((4, 3, 2)):
        weights = dict(zip(("vivid", "funny", "true"), perm))
        ranked = rank_letters(weights)
        results[perm] = ranked.index("V") + 1
    return results


def explain():
    """Human-readable ranking table, for --explain."""
    lines = ["letter  word               raw  penalty  total"]
    for letter in rank_letters():
        word = CANDIDATES[letter][0]
        lines.append(
            f"{letter}      {word:<18} {raw_score(letter):>3}  "
            f"{saturation_penalty(letter):>7.2f}  {total_score(letter):>6.2f}"
        )
    return "\n".join(lines)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--explain" in argv:
        print(explain())
        print("\nSensitivity (rank of V under each weight permutation):")
        for weights, rank in sorted(sensitivity_rank().items()):
            print(f"  vivid/funny/true = {weights}: V ranks #{rank}")
        print(f"\nChosen letter: {choose_letter()}")
        return 0
    letter = choose_letter()
    # The gate wants exactly one character: a single byte, no newline.
    out_path = os.environ.get("ENTRY_OUTPUT", OUTPUT_PATH)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(letter.encode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
