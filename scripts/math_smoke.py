"""Exercise the official Lines game; no optimisation or production publishing."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "math"
sys.path[:0] = [str(MATH / "games/0_0_lines"), str(MATH)]


def simulate(count):
    from game_config import GameConfig
    from gamestate import GameState
    from src.config import output_filenames

    # Keep test outputs separate from the official game's publish_files.
    output_filenames.PATH_TO_GAMES = str(ROOT / ".runtime/math-smoke")
    state = GameState(GameConfig())
    state.betmode = "base"
    for seed in range(count):
        state.criteria = "freegame" if seed == count - 1 else ("0" if seed % 3 == 0 else "basegame")
        state.run_spin(seed)
        book = state.book.to_json()
        assert isinstance(book["payoutMultiplier"], int)
        assert 0 <= book["payoutMultiplier"] <= round(state.config.wincap * 100)
        assert book["events"] and book["events"][0]["type"] == "reveal"
        assert [event["index"] for event in book["events"]] == list(range(len(book["events"])))
        assert book["id"] == seed
    return state


def main():
    import zstandard as zstd
    from src.write_data.write_data import write_json

    parser = argparse.ArgumentParser()
    parser.add_argument("--simulations", type=int, default=100, choices=range(10, 1001), metavar="10..1000")
    args = parser.parse_args()
    state = simulate(args.simulations)
    expected = state._library_lines.copy()
    replay = simulate(args.simulations)
    assert replay._library_lines == expected, "Seeded replay differs"
    output = ROOT / ".runtime/math-smoke"
    book_path = output / "books_base.jsonl.zst"
    write_json(state, str(book_path))
    restored = zstd.ZstdDecompressor().decompress(book_path.read_bytes()).decode().splitlines()
    assert restored == expected, "Compressed books do not round-trip"
    with (output / "lookUpTable_base_0.csv").open("w", newline="", encoding="utf-8") as stream:
        csv.writer(stream).writerows((json.loads(line)["id"], 1, json.loads(line)["payoutMultiplier"]) for line in restored)
    result = {
        "status": "passed", "example": "0_0_lines", "rounds": args.simulations,
        "seeded_replay": True, "compression_roundtrip": True,
        "freegame_events": any(e["type"] == "freeSpinTrigger" for line in expected for e in json.loads(line)["events"]),
        "books_sha256": hashlib.sha256(book_path.read_bytes()).hexdigest(),
        "purpose": "Conditional development smoke test; no RTP estimate or production approval.",
    }
    assert result["freegame_events"], "Free-spin path was not exercised"
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
