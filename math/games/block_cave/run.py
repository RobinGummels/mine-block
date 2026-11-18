"""Main file for generating a small, reproducible Block Cave prototype run.

Stage 2 math prototype only. This runs a modest, seeded set of simulations and
writes the books to a temporary JSONL. No optimisation, no analysis sheets, no
format checks and no production publishing.

Note on the `wincap` criteria: the `wincap` criteria distribution was removed
from `game_config.py`. Reaching the 1,000x cap on the exact design strips is
essentially impossible naturally (MATH_DESIGN.md §7, F4/F18), and the engine's
repeat-until-criteria loop never consumes `force_wincap`, so that distribution
could never converge. The 1,000x cap path itself is unchanged and is exercised
deterministically by `test_block_cave.py`, which constructs boards directly.
The `run.py` here runs the natural basegame, a forced freegame, and a couple of
zero-win criteria only.
"""

import json
from pathlib import Path

from gamestate import GameState
from game_config import GameConfig

ROOT = Path(__file__).resolve().parents[2]


def main():
    config = GameConfig()
    state = GameState(config)
    state.betmode = "base"

    # Small deterministic set: natural basegame spins, a forced freegame, and a
    # few zero-win criteria.
    criteria_seeds = (
        [("basegame", i) for i in range(40)]
        + [("freegame", i) for i in range(10)]
        + [("0", i) for i in range(10)]
    )

    books = []
    for criteria, seed in criteria_seeds:
        state.criteria = criteria
        state.run_spin(seed)
        books.append(state.book.to_json())

    out = ROOT / ".runtime" / "block_cave"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "prototype_books.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for b in books:
            f.write(json.dumps(b) + "\n")

    total = sum(b["payoutMultiplier"] for b in books)
    base_total = sum(b["baseGameWins"] for b in books)
    free_total = sum(b["freeGameWins"] for b in books)
    hit = sum(1 for b in books if b["payoutMultiplier"] > 0)
    max_win = max(b["payoutMultiplier"] for b in books)
    fs_entries = sum(1 for b in books if any(e["type"] == "freeSpinTrigger" for e in b["events"]))

    print(f"Rounds: {len(books)}")
    print(f"Total payoutMultiplier units: {total} (mean {total / len(books):.2f})")
    print(f"baseGameWins: {base_total:.2f}, freeGameWins: {free_total:.2f}")
    print(f"Hit (payoutMultiplier > 0): {hit} ({100.0 * hit / len(books):.1f}%)")
    print(f"Max payoutMultiplier: {max_win}")
    print(f"Free-spin trigger rounds: {fs_entries}")
    print("DEV observation only - NOT a measured RTP and NOT a confirmed hit frequency.")
    print(f"Wrote books to {path}")


if __name__ == "__main__":
    main()
