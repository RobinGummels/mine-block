"""Reproducible Stage 2 math prototype tests for Block Cave.

Run from the repo root:

    & "C:\\Users\\robin\\Documents\\stake\\stake-game-ai\\math\\.venv\\Scripts\\python.exe" \
        math\\games\\block_cave\\test_block_cave.py

These tests exercise the deterministic reels, book invariants, and the
game-specific mechanics (win, tumble, ore-vein upgrade, three-pickaxe trigger,
retrigger clamp, 1000x cap). They use small constructed boards and a handful of
natural seeded spins, and they do NOT measure RTP or hit frequency.

Note: the `wincap` criteria is exercised by constructing a board directly and
setting `running_bet_win` near the cap, because on the design strips the cap is
essentially unreachable naturally (MATH_DESIGN.md §7).
"""

import json
import sys
from pathlib import Path

BLOCK_CAVE_DIR = Path(__file__).resolve().parent
MATH_DIR = BLOCK_CAVE_DIR.parents[1]
sys.path.insert(0, str(BLOCK_CAVE_DIR))
sys.path.insert(0, str(MATH_DIR))

from game_config import GameConfig, build_strip, sha256_strip, BASE_COUNTS, FREE_COUNTS  # noqa: E402
from gamestate import GameState  # noqa: E402

BASE_SHA = "7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451"
FREE_SHA = "f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754"
WINCAP_UNITS = 100000


def fresh_state():
    config = GameConfig()
    state = GameState(config)
    state.betmode = "base"
    return state


def single_cascade(state, grid, criteria="basegame", emit_reveal=True):
    """Set a constructed board and drive exactly one cascade step.

    `grid` is a list (per reel) of lists (per row) of symbol-name strings.
    `draw_board` is called first so the reel infrastructure (reelstrip,
    reel_positions, top/bottom padding) is present for a potential tumble; the
    board is then overwritten with `grid`.
    """
    state.criteria = criteria
    state.reset_book()
    state.draw_board(emit_event=emit_reveal)
    state.board = [[state.create_symbol(name) for name in reel] for reel in grid]
    state.get_special_symbols_on_board()
    state.initial_scatter_count = state.count_special_symbols("scatter")
    state.initial_scatter_positions = [dict(p) for p in state.special_syms_on_board["scatter"]]
    state.get_clusters_update_wins()
    state.emit_tumble_win_events()
    return state.book.to_json()


def drive_cascade(state, grid, criteria="basegame", emit_reveal=True):
    """Set a constructed board and drive the FULL cascade to the final win.

    Mirrors `run_spin`'s inner loop (cascade -> set_end_tumble_event ->
    update_gametype_wins -> optional free spins -> evaluate_finalwin ->
    check_repeat -> imprint_wins) but operates on the constructed `grid`.
    """
    state.criteria = criteria
    state.reset_book()
    state.draw_board(emit_event=emit_reveal)
    state.board = [[state.create_symbol(name) for name in reel] for reel in grid]
    state.get_special_symbols_on_board()
    state.initial_scatter_count = state.count_special_symbols("scatter")
    state.initial_scatter_positions = [dict(p) for p in state.special_syms_on_board["scatter"]]
    state.get_clusters_update_wins()
    state.emit_tumble_win_events()
    while state.win_data["totalWin"] > 0 and not state.wincap_triggered:
        state.tumble_game_board()
        state.get_clusters_update_wins()
        state.emit_tumble_win_events()
    state.set_end_tumble_event()
    state.win_manager.update_gametype_wins(state.gametype)
    if state.check_fs_condition() and state.check_freespin_entry():
        state.run_freespin_from_base()
    state.evaluate_finalwin()
    state.check_repeat()
    state.imprint_wins()
    return state.book.to_json()


# ---------------------------------------------------------------------------
# 1. Deterministic reel strips
# ---------------------------------------------------------------------------

def test_strip_shas():
    base = build_strip(20261117, BASE_COUNTS)
    free = build_strip(20261118, FREE_COUNTS)
    assert len(base) == 200, f"base strip length {len(base)} != 200"
    assert len(free) == 200, f"free strip length {len(free)} != 200"
    assert sha256_strip(base) == BASE_SHA, "base strip SHA-256 mismatch"
    assert sha256_strip(free) == FREE_SHA, "free strip SHA-256 mismatch"
    for sym, c in BASE_COUNTS.items():
        assert base.count(sym) == c, f"base {sym} count {base.count(sym)} != {c}"
    for sym, c in FREE_COUNTS.items():
        assert free.count(sym) == c, f"free {sym} count {free.count(sym)} != {c}"
    # determinism: rebuilding yields the identical list
    assert build_strip(20261117, BASE_COUNTS) == base, "base strip not deterministic"
    assert build_strip(20261118, FREE_COUNTS) == free, "free strip not deterministic"
    print("  [ok] strips reproduce documented SHA-256 + counts")


# ---------------------------------------------------------------------------
# 2. Book invariants
# ---------------------------------------------------------------------------

def _check_book_invariants(b, label):
    # payout is an integer within [0, 100000]
    assert isinstance(b["payoutMultiplier"], int), f"{label}: payoutMultiplier not int"
    assert 0 <= b["payoutMultiplier"] <= WINCAP_UNITS, f"{label}: payout out of range"
    # event indexes are contiguous starting at 0
    for i, e in enumerate(b["events"]):
        assert e["index"] == i, f"{label}: event index not contiguous at {i}"
    # first event is reveal
    assert b["events"][0]["type"] == "reveal", f"{label}: first event not reveal"
    # payoutMultiplier matches the finalWin amount
    final_amounts = [e["amount"] for e in b["events"] if e["type"] == "finalWin"]
    assert final_amounts, f"{label}: no finalWin event"
    assert final_amounts[-1] == b["payoutMultiplier"], f"{label}: finalWin != payoutMultiplier"
    # base+free (in multiplier units) capped at wincap -> payoutMultiplier
    total_mult = b["baseGameWins"] + b["freeGameWins"]
    assert int(round(min(total_mult, 1000.0) * 100, 0)) == b["payoutMultiplier"], (
        f"{label}: base+free cap mismatch ({total_mult})"
    )
    assert b["baseGameWins"] >= 0 and b["freeGameWins"] >= 0, f"{label}: negative wins"


def test_book_invariants():
    config = GameConfig()
    state = GameState(config)
    state.betmode = "base"
    ran = 0
    for criteria in ("basegame", "freegame", "0"):
        for seed in (0, 1, 2):
            state.criteria = criteria
            state.run_spin(seed)
            b = state.book.to_json()
            _check_book_invariants(b, f"{criteria}#{seed}")
            ran += 1
    print(f"  [ok] book invariants across {ran} spins (basegame/freegame/0)")


# ---------------------------------------------------------------------------
# 3. Win (winInfo + setWin + setTotalWin)
# ---------------------------------------------------------------------------

def test_win_event_sequence():
    state = fresh_state()
    # A single 5-cluster of earth in reel 0 (rows 0-4) plus a vein wild,
    # with the rest of the board filled so nothing else clusters.
    grid = [
        ["earth", "earth", "earth", "earth", "earth"],
        ["ore_vein", "stone", "timber", "copper", "silver"],
        ["timber", "copper", "timber", "copper", "timber"],
        ["copper", "timber", "copper", "timber", "copper"],
        ["timber", "copper", "timber", "copper", "timber"],
        ["copper", "timber", "copper", "timber", "copper"],
    ]
    b = drive_cascade(state, grid, criteria="basegame")
    types = [e["type"] for e in b["events"]]
    assert "winInfo" in types, f"no winInfo: {types}"
    assert "setWin" in types, f"no setWin: {types}"
    assert "setTotalWin" in types, f"no setTotalWin: {types}"
    # winInfo must come before setWin and setTotalWin
    wi = types.index("winInfo")
    sw = types.index("setWin")
    st = types.index("setTotalWin")
    assert wi < sw < st, f"win event order wrong: {types}"
    # the first win is the earth 6-cluster (5 earth + vein wild)
    win_infos = [e for e in b["events"] if e["type"] == "winInfo"]
    assert win_infos, "no winInfo event"
    first_win = win_infos[0]["wins"][0]
    assert first_win["symbol"] == "earth", first_win
    assert first_win["clusterSize"] == 6, f"expected a 6-cluster, got {first_win['clusterSize']}"
    print("  [ok] win emits winInfo -> setWin -> setTotalWin (earth 6-cluster)")


# ---------------------------------------------------------------------------
# 4. Tumble (>=2 winInfo with tumbleBoard between)
# ---------------------------------------------------------------------------

def test_tumble_between_wins():
    config = GameConfig()
    state = GameState(config)
    state.betmode = "base"
    state.criteria = "basegame"
    found = None
    for seed in range(400):
        state.run_spin(seed)
        b = state.book.to_json()
        wi = [i for i, e in enumerate(b["events"]) if e["type"] == "winInfo"]
        if len(wi) >= 2:
            found = (seed, b)
            break
    assert found, "no basegame spin with >=2 winInfo in 400 seeds"
    seed, b = found
    wi = [i for i, e in enumerate(b["events"]) if e["type"] == "winInfo"]
    for a, c in zip(wi, wi[1:]):
        between = [e["type"] for e in b["events"][a + 1:c]]
        assert "tumbleBoard" in between, f"no tumbleBoard between winInfo@{a} and {c}: {between}"
    # every tumbleBoard removes at least one symbol
    for e in b["events"]:
        if e["type"] == "tumbleBoard":
            assert len(e["explodingSymbols"]) > 0, "tumbleBoard with no exploding symbols"
    print(f"  [ok] tumble: {len(wi)} winInfo with tumbleBoard between (seed {seed})")


# ---------------------------------------------------------------------------
# 5. Ore-vein upgrade
# ---------------------------------------------------------------------------

def test_ore_vein_upgrade_with_target():
    """Vein in a winning cluster with an eligible adjacent block => 1 upgrade."""
    state = fresh_state()
    grid = [
        ["earth", "earth", "earth", "earth", "earth"],
        ["ore_vein", "stone", "timber", "copper", "silver"],
        ["timber", "copper", "timber", "copper", "timber"],
        ["copper", "timber", "copper", "timber", "copper"],
        ["timber", "copper", "timber", "copper", "timber"],
        ["copper", "timber", "copper", "timber", "copper"],
    ]
    b = single_cascade(state, grid, criteria="basegame")
    upgrades = [e for e in b["events"] if e["type"] == "oreVeinUpgrade"]
    assert upgrades, "no oreVeinUpgrade event"
    ev = upgrades[0]
    # vein at (reel 1, row 0) activates; padded row = 1
    assert len(ev["veinPositions"]) == 1, f"expected 1 vein, got {ev['veinPositions']}"
    assert ev["veinPositions"][0] == {"reel": 1, "row": 1}, ev["veinPositions"]
    # first eligible neighbour in scan order (up, down, left, right) is the
    # `stone` directly below (reel 1, row 1) => upgraded to diamond, padded row 2
    assert len(ev["upgrades"]) == 1, f"expected 1 upgrade, got {ev['upgrades']}"
    assert ev["upgrades"][0] == {"reel": 1, "row": 2, "symbol": "diamond"}, ev["upgrades"]
    # the board cell was actually converted to diamond
    assert state.board[1][1].name == "diamond", "upgrade target not converted to diamond"
    # event order: updateTumbleWin < oreVeinUpgrade < tumbleBoard (if present)
    types = [e["type"] for e in b["events"]]
    assert "updateTumbleWin" in types
    ut = types.index("updateTumbleWin")
    ov = types.index("oreVeinUpgrade")
    assert ut < ov, f"oreVeinUpgrade not after updateTumbleWin: {types}"
    print("  [ok] ore-vein upgrade converts 1 eligible adjacent block to diamond")


def test_ore_vein_upgrade_no_target():
    """Vein in a winning cluster with all-ineligible neighbours => no upgrade,
    but still listed in veinPositions (activation happened)."""
    state = fresh_state()
    # Diamond 5-cluster in reel 0; vein at (1,1); all 4 orthogonal neighbours
    # are diamond (ineligible) or pickaxe (ineligible).
    grid = [
        ["diamond", "diamond", "diamond", "diamond", "diamond"],
        ["diamond", "ore_vein", "diamond", "gold", "silver"],
        ["pickaxe", "pickaxe", "copper", "timber", "copper"],
        ["copper", "timber", "copper", "timber", "copper"],
        ["timber", "copper", "timber", "copper", "timber"],
        ["copper", "timber", "copper", "timber", "copper"],
    ]
    b = single_cascade(state, grid, criteria="basegame")
    upgrades = [e for e in b["events"] if e["type"] == "oreVeinUpgrade"]
    assert upgrades, "expected an oreVeinUpgrade event for the activated vein"
    ev = upgrades[0]
    assert len(ev["veinPositions"]) == 1, f"expected 1 vein, got {ev['veinPositions']}"
    assert ev["veinPositions"][0] == {"reel": 1, "row": 2}, ev["veinPositions"]
    # No eligible adjacent regular block => no upgrades
    assert ev["upgrades"] == [], f"expected no upgrades, got {ev['upgrades']}"
    print("  [ok] ore-vein activation with no eligible target => veinPositions only")


# ---------------------------------------------------------------------------
# 6. Three-pickaxe free-spin trigger
# ---------------------------------------------------------------------------

def test_three_pickaxe_trigger():
    config = GameConfig()
    state = GameState(config)
    state.betmode = "base"
    state.criteria = "freegame"
    state.run_spin(0)
    b = state.book.to_json()
    triggers = [e for e in b["events"] if e["type"] == "freeSpinTrigger"]
    assert triggers, "no freeSpinTrigger for forced 3-pickaxe board"
    assert triggers[0]["totalFs"] in (8, 12, 16), f"unexpected totalFs {triggers[0]['totalFs']}"
    # 3 pickaxes => 8 starting spins
    assert triggers[0]["totalFs"] == 8, triggers[0]
    # positions reflect the initial board (padded row)
    assert len(triggers[0]["positions"]) >= 3, triggers[0]
    # free spins use the freegame type (FR0 strip) -> reveals with gameType freegame
    free_reveals = [e for e in b["events"] if e["type"] == "reveal" and e["gameType"] == "freegame"]
    assert len(free_reveals) >= 8, f"expected >=8 free-game reveals, got {len(free_reveals)}"
    # config maps freegame_type to FR0
    freegame_conditions = [d for d in config.bet_modes[0].get_distributions() if d._criteria == "freegame"][0]
    assert freegame_conditions._conditions["reel_weights"]["freegame"] == {"FR0": 1}, "freegame not using FR0"
    assert "freeSpinEnd" in [e["type"] for e in b["events"]], "no freeSpinEnd"
    print(f"  [ok] 3 pickaxes trigger freeSpinTrigger totalFs=8, {len(free_reveals)} free reveals on FR0")


# ---------------------------------------------------------------------------
# 7. Natural free-spin triggering (no suppression)
# ---------------------------------------------------------------------------

def test_natural_trigger():
    """A basegame board with 3+ pickaxes must trigger free spins naturally
    (the draw_board re-draw suppression loop is removed)."""
    config = GameConfig()
    state = GameState(config)
    state.betmode = "base"
    state.criteria = "basegame"
    found = None
    for seed in range(500):
        state.run_spin(seed)
        b = state.book.to_json()
        if any(e["type"] == "freeSpinTrigger" for e in b["events"]):
            found = (seed, b)
            break
    assert found, "no natural basegame free-spin trigger in 500 seeds"
    seed, b = found
    trig = [e for e in b["events"] if e["type"] == "freeSpinTrigger"]
    assert trig, "no freeSpinTrigger"
    assert trig[0]["totalFs"] in (8, 12, 16), f"unexpected totalFs {trig[0]['totalFs']}"
    # the base spin was NOT forced (force_freegame is False for basegame criteria)
    assert not config.bet_modes[0].get_distributions()[0]._conditions["force_freegame"]
    print(f"  [ok] natural trigger at basegame seed {seed}, totalFs={trig[0]['totalFs']}")


# ---------------------------------------------------------------------------
# 8. Retrigger clamp to 60
# ---------------------------------------------------------------------------

def test_retrigger_clamp():
    config = GameConfig()
    state = GameState(config)
    state.betmode = "base"
    state.criteria = "freegame"
    state.reset_book()
    state.refresh_special_syms()
    state.gametype = config.freegame_type
    state.initial_scatter_count = 3
    state.initial_scatter_positions = [{"reel": 0, "row": 0}, {"reel": 1, "row": 1}, {"reel": 2, "row": 2}]
    state.special_syms_on_board["scatter"] = [dict(p) for p in state.initial_scatter_positions]

    # 55 + 8 = 63 -> clamp to 60
    state.tot_fs = 55
    state.update_fs_retrigger_amt()
    assert state.tot_fs == 60, f"retrigger not clamped to 60, got {state.tot_fs}"
    trig = [e for e in state.book.events if e["type"] == "freeSpinRetrigger"]
    assert trig and trig[-1]["totalFs"] == 60, trig

    # high pickaxe count clamps to 6 -> 16 added; 50 + 16 = 66 -> clamp 60
    state.reset_book()
    state.tot_fs = 50
    state.initial_scatter_count = 8  # clamp to 6
    state.update_fs_retrigger_amt()
    assert state.tot_fs == 60, f"retrigger with 8 pickaxes not clamped to 60, got {state.tot_fs}"
    print("  [ok] retrigger clamps total free spins to 60")


# ---------------------------------------------------------------------------
# 9. 1000x cap
# ---------------------------------------------------------------------------

def test_wincap():
    config = GameConfig()
    state = GameState(config)
    state.betmode = "base"
    state.criteria = "basegame"
    state.reset_book()
    state.draw_board(emit_event=True)
    # A full board of ingot => one 30-cluster paying 125x, enough to cross the cap.
    grid = [["ingot"] * 5 for _ in range(6)]
    state.board = [[state.create_symbol(name) for name in reel] for reel in grid]
    state.get_special_symbols_on_board()
    state.initial_scatter_count = 0
    state.initial_scatter_positions = []
    # Start the cumulative round total just below the cap.
    state.win_manager.running_bet_win = 999.0
    state.win_manager.basegame_wins = 999.0
    state.win_manager.spin_win = 0.0

    state.get_clusters_update_wins()
    state.emit_tumble_win_events()

    # The 30-cluster win crosses the cap mid-cascade.
    assert state.wincap_triggered, "wincap not triggered"
    types = [e["type"] for e in state.book.events]
    assert "wincap" in types, f"no wincap event: {types}"
    ut = types.index("updateTumbleWin")
    wc = types.index("wincap")
    assert ut < wc, f"wincap not after updateTumbleWin: {types}"

    state.set_end_tumble_event()
    state.win_manager.update_gametype_wins(state.gametype)
    if state.check_fs_condition() and state.check_freespin_entry():
        state.run_freespin_from_base()
    state.evaluate_finalwin()
    state.check_repeat()
    state.imprint_wins()
    b = state.book.to_json()

    total_events = [e for e in b["events"] if e["type"] == "setTotalWin"]
    final_events = [e for e in b["events"] if e["type"] == "finalWin"]
    assert total_events and total_events[-1]["amount"] == WINCAP_UNITS, total_events
    assert final_events and final_events[-1]["amount"] == WINCAP_UNITS, final_events
    assert b["payoutMultiplier"] == WINCAP_UNITS, b["payoutMultiplier"]
    print("  [ok] 1000x cap clamps setTotalWin/finalWin/payoutMultiplier to 100000")


# ---------------------------------------------------------------------------
# 10. wincap + ore-vein upgrade in the same cascade
# ---------------------------------------------------------------------------

def test_wincap_ore_vein_upgrade():
    """A single cascade that crosses the 1,000x cap AND activates an ore-vein.

    Regression guard for the emission order in `emit_tumble_win_events`
    (MATH_DESIGN.md §8): `winInfo` -> `updateTumbleWin` -> `wincap` ->
    `oreVeinUpgrade`. The ore-vein upgrade must still be processed in the same
    cascade step that triggers the wincap, and the cascade must then stop
    (`wincap_triggered` halts the tumble loop, so no `tumbleBoard` follows).
    """
    config = GameConfig()
    state = GameState(config)
    state.betmode = "base"
    state.criteria = "basegame"
    state.reset_book()
    state.draw_board(emit_event=True)

    # Full ingot board (one 30-cluster paying 125x) with a single ore-vein wild
    # at (reel 1, row 0) inside the winning cluster.
    grid = [["ingot"] * 5 for _ in range(6)]
    grid[1][0] = "ore_vein"
    state.board = [[state.create_symbol(name) for name in reel] for reel in grid]
    state.get_special_symbols_on_board()
    state.initial_scatter_count = 0
    state.initial_scatter_positions = []

    # Start the cumulative round total just below the cap so this single cascade
    # crosses it (999 + 125 = 1124 >= 1000).
    state.win_manager.running_bet_win = 999.0
    state.win_manager.basegame_wins = 999.0
    state.win_manager.spin_win = 0.0

    state.get_clusters_update_wins()
    state.emit_tumble_win_events()

    # wincap must have triggered mid-cascade.
    assert state.wincap_triggered, "wincap not triggered in the same cascade"

    types = [e["type"] for e in state.book.events]
    assert "updateTumbleWin" in types, f"no updateTumbleWin: {types}"
    assert "wincap" in types, f"no wincap event: {types}"
    assert "oreVeinUpgrade" in types, f"no oreVeinUpgrade event: {types}"
    ut = types.index("updateTumbleWin")
    wc = types.index("wincap")
    ov = types.index("oreVeinUpgrade")
    assert ut < wc < ov, f"expected updateTumbleWin < wincap < oreVeinUpgrade, got {types}"

    # wincap event carries the capped amount in ×100 units.
    wincap_events = [e for e in state.book.events if e["type"] == "wincap"]
    assert wincap_events, "no wincap event"
    assert wincap_events[0]["amount"] == WINCAP_UNITS, (
        f"wincap amount {wincap_events[0]['amount']} != {WINCAP_UNITS}"
    )

    # ore-vein upgrade: the vein at (reel 1, row 0) activates (padded row 1);
    # its first eligible neighbour (down, (1,1)) becomes diamond (padded row 2).
    ov_event = [e for e in state.book.events if e["type"] == "oreVeinUpgrade"][0]
    assert ov_event["veinPositions"] == [{"reel": 1, "row": 1}], ov_event
    assert ov_event["upgrades"] == [{"reel": 1, "row": 2, "symbol": "diamond"}], ov_event
    assert state.board[1][1].name == "diamond", "upgrade target not converted to diamond"

    # The cascade must stop after the wincap: no tumbleBoard may follow.
    assert "tumbleBoard" not in types, f"cascade continued past wincap: {types}"

    # Drive the rest of the round to confirm the final win is capped at 100000.
    state.set_end_tumble_event()
    state.win_manager.update_gametype_wins(state.gametype)
    if state.check_fs_condition() and state.check_freespin_entry():
        state.run_freespin_from_base()
    state.evaluate_finalwin()
    state.check_repeat()
    state.imprint_wins()
    b = state.book.to_json()

    total_events = [e for e in b["events"] if e["type"] == "setTotalWin"]
    final_events = [e for e in b["events"] if e["type"] == "finalWin"]
    assert total_events and total_events[-1]["amount"] == WINCAP_UNITS, total_events
    assert final_events and final_events[-1]["amount"] == WINCAP_UNITS, final_events
    assert b["payoutMultiplier"] == WINCAP_UNITS, b["payoutMultiplier"]
    # book invariants still hold (base+free sum-then-cap)
    _check_book_invariants(b, "wincap+oreVeinUpgrade")
    print("  [ok] wincap + oreVeinUpgrade order updateTumbleWin->wincap->oreVeinUpgrade, "
          "capped 100000, cascade stops")


# ---------------------------------------------------------------------------
# 11. create-cluster ore-vein rule (Stage 3 variant, DEV rule)
# ---------------------------------------------------------------------------

def _create_cluster_state():
    """A state whose config uses the `create-cluster` ore-vein rule.

    The rule is applied on the config singleton; the caller must restore the
    baseline rule after use (see each test's `finally`).
    """
    config = GameConfig()
    config.ore_vein_rule = "create-cluster"
    config.ore_vein_target = "diamond"
    state = GameState(config)
    state.betmode = "base"
    return state, config


def test_create_cluster_rule_converts_when_paying_cluster():
    """create-cluster converts an eligible neighbour ONLY IF it creates a paying
    (>=5) target cluster among surviving blocks.

    Board: an earth 5-cluster + vein (winning cluster, 6 cells). The vein's first
    eligible neighbour (down, (1,1)) is a stone; converting it to diamond joins
    the existing diamond cells (1,2),(1,3),(2,0),(2,1) into a 5-diamond cluster
    that survives the tumble, so the conversion is applied.
    """
    state, config = _create_cluster_state()
    try:
        grid = [
            ["earth", "earth", "earth", "earth", "earth"],
            ["ore_vein", "stone", "diamond", "diamond", "silver"],
            ["diamond", "diamond", "copper", "timber", "copper"],
            ["timber", "copper", "timber", "copper", "timber"],
            ["copper", "timber", "copper", "timber", "copper"],
            ["timber", "copper", "timber", "copper", "timber"],
        ]
        b = single_cascade(state, grid, criteria="basegame")
        upgrades = [e for e in b["events"] if e["type"] == "oreVeinUpgrade"]
        assert upgrades, "no oreVeinUpgrade event"
        ev = upgrades[0]
        # vein at (reel 1, row 0) activates -> padded row 1
        assert ev["veinPositions"] == [{"reel": 1, "row": 1}], ev["veinPositions"]
        # (1,1) stone -> diamond, padded row 2
        assert ev["upgrades"] == [{"reel": 1, "row": 2, "symbol": "diamond"}], ev["upgrades"]
        assert state.board[1][1].name == "diamond", "upgrade target not converted to diamond"
        print("  [ok] create-cluster converts an eligible neighbour that completes a >=5 cluster")
    finally:
        config.ore_vein_rule = "baseline"
        config.ore_vein_target = "diamond"


def test_create_cluster_rule_no_convert_without_cluster():
    """create-cluster does NOT convert when the conversion would not create a
    paying (>=5) target cluster, but the vein still activates (veinPositions)."""
    state, config = _create_cluster_state()
    try:
        grid = [
            ["earth", "earth", "earth", "earth", "earth"],
            ["ore_vein", "stone", "stone", "stone", "silver"],
            ["timber", "copper", "timber", "copper", "timber"],
            ["copper", "timber", "copper", "timber", "copper"],
            ["timber", "copper", "timber", "copper", "timber"],
            ["copper", "timber", "copper", "timber", "copper"],
        ]
        b = single_cascade(state, grid, criteria="basegame")
        upgrades = [e for e in b["events"] if e["type"] == "oreVeinUpgrade"]
        assert upgrades, "expected an oreVeinUpgrade event for the activated vein"
        ev = upgrades[0]
        assert ev["veinPositions"] == [{"reel": 1, "row": 1}], ev["veinPositions"]
        # The eligible neighbour (1,1) stone would only become a 1-cell diamond
        # (no target/vein survivors adjacent) -> not a paying cluster -> no convert.
        assert ev["upgrades"] == [], f"expected no upgrades, got {ev['upgrades']}"
        assert state.board[1][1].name == "stone", "cell should not be converted"
        print("  [ok] create-cluster does not convert without a >=5 target cluster, "
              "but vein activation is recorded")
    finally:
        config.ore_vein_rule = "baseline"
        config.ore_vein_target = "diamond"


def test_ore_vein_rule_dispatch():
    """Rule dispatch: `config.ore_vein_rule` selects the rule; unknown names fall
    back to the baseline rule."""
    from ore_vein_rules import get_rule
    assert get_rule("create-cluster").__name__ == "rule_create_cluster", "create-cluster not registered"
    assert get_rule("baseline").__name__ == "rule_baseline", "baseline not registered"
    assert get_rule("no-such-rule").__name__ == "rule_baseline", "unknown rule should default to baseline"
    # The executable reads the rule name from the config attribute.
    config = GameConfig()
    config.ore_vein_rule = "create-cluster"
    from game_executables import _ore_target
    assert _ore_target(config) == "diamond", "default ore target should be diamond"
    config.ore_vein_rule = "baseline"
    print("  [ok] ore-vein rule dispatch (create-cluster/baseline/unknown->baseline)")


# ---------------------------------------------------------------------------
# 12. Stage-3 variant config (DEV, separate config module)
# ---------------------------------------------------------------------------

def test_variant_config_reproducible():
    """The Stage-3 variant config produces deterministic strips (length 200,
    counts + SHA-256) and a config with the variant reels and ore-vein rule.

    The baseline `game_config.py` must remain unchanged (its strips/SHAs are
    checked in `test_strip_shas`). The variant config singleton is reset here
    and the baseline rule restored afterward so later tests see the baseline.
    """
    import variant_config as vc
    from game_config import GameConfig

    base, free = vc.build_strips()
    assert len(base) == 200 and len(free) == 200, "variant strips must be length 200"
    for sym, c in vc.BASE_COUNTS.items():
        assert base.count(sym) == c, f"variant base {sym} count {base.count(sym)} != {c}"
    for sym, c in vc.FREE_COUNTS.items():
        assert free.count(sym) == c, f"variant free {sym} count {free.count(sym)} != {c}"
    bs, fs = vc.sha256()
    assert bs == vc.BASE_SHA, f"variant base SHA mismatch {bs}"
    assert fs == vc.FREE_SHA, f"variant free SHA mismatch {fs}"
    # determinism
    assert vc.build_strips()[0] == base, "variant base strip not deterministic"
    assert vc.build_strips()[1] == free, "variant free strip not deterministic"

    # build_config returns an independent config with the variant reels/rule.
    cfg = vc.build_config()
    assert cfg.ore_vein_rule == "create-cluster", "variant ore-vein rule not set"
    assert cfg.ore_vein_target == "diamond", "variant ore-vein target not set"
    # reels hold the variant strips (all six share the strip, as in baseline)
    assert all(cfg.reels["BR0"][0] == base for _ in range(cfg.num_reels)), "variant BR0 wrong"
    assert all(cfg.reels["FR0"][0] == free for _ in range(cfg.num_reels)), "variant FR0 wrong"
    # restore the baseline singleton for any subsequent test
    GameConfig._instance = None
    _ = GameConfig()
    print("  [ok] variant config reproducible (strips + SHAs + ore-vein rule)")

    # The baseline config must still reproduce its own strips (unchanged).
    assert sha256_strip(build_strip(20261117, BASE_COUNTS)) == BASE_SHA, "baseline base SHA changed"
    assert sha256_strip(build_strip(20261118, FREE_COUNTS)) == FREE_SHA, "baseline free SHA changed"
    print("  [ok] baseline strips unchanged after variant config build")


# ---------------------------------------------------------------------------
# 13. Stage-3 Candidate 2 config (DEV, separate config module)
# ---------------------------------------------------------------------------

def test_candidate2_config_reproducible():
    """The Stage-3 Candidate 2 config produces deterministic strips (length 200,
    counts + SHA-256) and a config with the candidate reels and ore-vein rule.

    The baseline `game_config.py` and the Stage-3 `variant_config.py` must
    remain unchanged (their strips/SHAs are checked elsewhere). The candidate
    config singleton is reset here and the baseline rule restored afterward so
    later tests see the baseline.
    """
    import candidate2_config as cc
    from game_config import GameConfig

    base, free = cc.build_strips()
    assert len(base) == 200 and len(free) == 200, "Candidate 2 strips must be length 200"
    for sym, c in cc.BASE_COUNTS.items():
        assert base.count(sym) == c, f"Candidate 2 base {sym} count {base.count(sym)} != {c}"
    for sym, c in cc.FREE_COUNTS.items():
        assert free.count(sym) == c, f"Candidate 2 free {sym} count {free.count(sym)} != {c}"
    bs, fs = cc.sha256()
    assert bs == cc.BASE_SHA, f"Candidate 2 base SHA mismatch {bs}"
    assert fs == cc.FREE_SHA, f"Candidate 2 free SHA mismatch {fs}"
    # determinism
    assert cc.build_strips()[0] == base, "Candidate 2 base strip not deterministic"
    assert cc.build_strips()[1] == free, "Candidate 2 free strip not deterministic"

    # build_config returns an independent config with the candidate reels/rule.
    cfg = cc.build_config()
    assert cfg.ore_vein_rule == "create-cluster", "Candidate 2 ore-vein rule not set"
    assert cfg.ore_vein_target == "diamond", "Candidate 2 ore-vein target not set"
    # reels hold the candidate strips (all six share the strip, as in baseline)
    assert all(cfg.reels["BR0"][0] == base for _ in range(cfg.num_reels)), "Candidate 2 BR0 wrong"
    assert all(cfg.reels["FR0"][0] == free for _ in range(cfg.num_reels)), "Candidate 2 FR0 wrong"
    # restore the baseline singleton for any subsequent test
    GameConfig._instance = None
    _ = GameConfig()
    print("  [ok] Candidate 2 config reproducible (strips + SHAs + ore-vein rule)")

    # The baseline config must still reproduce its own strips (unchanged).
    assert sha256_strip(build_strip(20261117, BASE_COUNTS)) == BASE_SHA, "baseline base SHA changed"
    assert sha256_strip(build_strip(20261118, FREE_COUNTS)) == FREE_SHA, "baseline free SHA changed"
    print("  [ok] baseline strips unchanged after Candidate 2 config build")


def test_candidate_a_config_reproducible():
    """The Stage-3 Candidate A config produces deterministic strips (length 200,
    counts + SHA-256) and a config with the candidate reels and ore-vein rule.

    Candidate A reuses the §3.1 base seed/pickaxe/ore_vein count and applies the
    DEV `create-cluster` rule. The baseline and other candidates must remain
    unchanged. The candidate config singleton is reset here and the baseline rule
    restored afterward so later tests see the baseline.
    """
    import candidate_a_config as ca
    from game_config import GameConfig

    base, free = ca.build_strips()
    assert len(base) == 200 and len(free) == 200, "Candidate A strips must be length 200"
    for sym, c in ca.BASE_COUNTS.items():
        assert base.count(sym) == c, f"Candidate A base {sym} count {base.count(sym)} != {c}"
    for sym, c in ca.FREE_COUNTS.items():
        assert free.count(sym) == c, f"Candidate A free {sym} count {free.count(sym)} != {c}"
    bs, fs = ca.sha256()
    assert bs == ca.BASE_SHA, f"Candidate A base SHA mismatch {bs}"
    assert fs == ca.FREE_SHA, f"Candidate A free SHA mismatch {fs}"
    assert ca.build_strips()[0] == base, "Candidate A base strip not deterministic"
    assert ca.build_strips()[1] == free, "Candidate A free strip not deterministic"

    cfg = ca.build_config()
    assert cfg.ore_vein_rule == "create-cluster", "Candidate A ore-vein rule not set"
    assert cfg.ore_vein_target == "diamond", "Candidate A ore-vein target not set"
    assert all(cfg.reels["BR0"][0] == base for _ in range(cfg.num_reels)), "Candidate A BR0 wrong"
    assert all(cfg.reels["FR0"][0] == free for _ in range(cfg.num_reels)), "Candidate A FR0 wrong"
    GameConfig._instance = None
    _ = GameConfig()
    print("  [ok] Candidate A config reproducible (strips + SHAs + ore-vein rule)")

    assert sha256_strip(build_strip(20261117, BASE_COUNTS)) == BASE_SHA, "baseline base SHA changed"
    assert sha256_strip(build_strip(20261118, FREE_COUNTS)) == FREE_SHA, "baseline free SHA changed"
    print("  [ok] baseline strips unchanged after Candidate A config build")


def test_candidate_b_config_reproducible():
    """The Stage-3 Candidate B config produces deterministic strips (length 200,
    counts + SHA-256) and a config with the candidate reels and ore-vein rule.

    Candidate B removes Silver Ore (silver=0) and rebalances to sum 200, and
    applies the DEV `create-cluster` rule. The baseline and other candidates must
    remain unchanged. The candidate config singleton is reset here and the
    baseline rule restored afterward so later tests see the baseline.
    """
    import candidate_b_config as cb
    from game_config import GameConfig

    base, free = cb.build_strips()
    assert len(base) == 200 and len(free) == 200, "Candidate B strips must be length 200"
    assert cb.BASE_COUNTS["silver"] == 0, "Candidate B must remove silver"
    assert sum(cb.BASE_COUNTS.values()) == 200, "Candidate B base must sum to 200"
    for sym, c in cb.BASE_COUNTS.items():
        assert base.count(sym) == c, f"Candidate B base {sym} count {base.count(sym)} != {c}"
    for sym, c in cb.FREE_COUNTS.items():
        assert free.count(sym) == c, f"Candidate B free {sym} count {free.count(sym)} != {c}"
    bs, fs = cb.sha256()
    assert bs == cb.BASE_SHA, f"Candidate B base SHA mismatch {bs}"
    assert fs == cb.FREE_SHA, f"Candidate B free SHA mismatch {fs}"
    assert cb.build_strips()[0] == base, "Candidate B base strip not deterministic"
    assert cb.build_strips()[1] == free, "Candidate B free strip not deterministic"

    cfg = cb.build_config()
    assert cfg.ore_vein_rule == "create-cluster", "Candidate B ore-vein rule not set"
    assert cfg.ore_vein_target == "diamond", "Candidate B ore-vein target not set"
    assert all(cfg.reels["BR0"][0] == base for _ in range(cfg.num_reels)), "Candidate B BR0 wrong"
    assert all(cfg.reels["FR0"][0] == free for _ in range(cfg.num_reels)), "Candidate B FR0 wrong"
    GameConfig._instance = None
    _ = GameConfig()
    print("  [ok] Candidate B config reproducible (strips + SHAs + ore-vein rule)")

    assert sha256_strip(build_strip(20261117, BASE_COUNTS)) == BASE_SHA, "baseline base SHA changed"
    assert sha256_strip(build_strip(20261118, FREE_COUNTS)) == FREE_SHA, "baseline free SHA changed"
    print("  [ok] baseline strips unchanged after Candidate B config build")


def test_lapis_config_reproducible():
    """The Lapis Lazuli config is a mathematically-neutral rename of Candidate A.

    It replaces `silver` with `lapis` at the SAME position in the non-common
    order and with the SAME counts, so the generated strips differ from
    Candidate A's strips ONLY by the literal `silver` -> `lapis` rename, and the
    paytable gives `lapis` exactly Candidate A's `silver` row. The baseline
    `game_config.py` strips/SHAs must remain byte-identical.
    """
    import candidate_a_config as ca
    import candidate_lapis_config as lc
    from game_config import GameConfig

    # 1. Lapis strips are deterministic, length 200, counts + SHAs match.
    base, free = lc.build_lapis_strips()
    assert len(base) == 200 and len(free) == 200, "Lapis strips must be length 200"
    for sym, c in lc.BASE_COUNTS.items():
        assert base.count(sym) == c, f"Lapis base {sym} count {base.count(sym)} != {c}"
    for sym, c in lc.FREE_COUNTS.items():
        assert free.count(sym) == c, f"Lapis free {sym} count {free.count(sym)} != {c}"
    bs, fs = lc.sha256()
    assert bs == lc.BASE_SHA, f"Lapis base SHA mismatch {bs}"
    assert fs == lc.FREE_SHA, f"Lapis free SHA mismatch {fs}"
    assert lc.build_lapis_strips()[0] == base, "Lapis base strip not deterministic"
    assert lc.build_lapis_strips()[1] == free, "Lapis free strip not deterministic"

    # 2. Lapis strips differ from Candidate A ONLY by the silver -> lapis rename.
    cand_a_base, cand_a_free = ca.build_strips()
    assert [s.replace("lapis", "silver") for s in base] == cand_a_base, (
        "Lapis base strip != Candidate A base after silver->lapis rename"
    )
    assert [s.replace("lapis", "silver") for s in free] == cand_a_free, (
        "Lapis free strip != Candidate A free after silver->lapis rename"
    )
    # Position-by-position: every position either matches, or is (lapis, silver).
    assert all((s == a) or (s == "lapis" and a == "silver") for s, a in zip(base, cand_a_base))
    assert all((s == a) or (s == "lapis" and a == "silver") for s, a in zip(free, cand_a_free))
    # No silver remains in the lapis strips, and the lapis count equals A's silver count.
    assert "silver" not in base and "silver" not in free, "silver must be fully removed"
    assert base.count("lapis") == cand_a_base.count("silver"), "lapis base count != silver count"
    assert free.count("lapis") == cand_a_free.count("silver"), "lapis free count != silver count"

    # 3. build_config returns an independent config with lapis reels/rule and a
    #    paytable that gives `lapis` exactly Candidate A's `silver` row.
    cfg = lc.build_config()
    assert cfg.ore_vein_rule == "create-cluster", "Lapis ore-vein rule not set"
    assert cfg.ore_vein_target == "diamond", "Lapis ore-vein target not set"
    assert all(cfg.reels["BR0"][0] == base for _ in range(cfg.num_reels)), "Lapis BR0 wrong"
    assert all(cfg.reels["FR0"][0] == free for _ in range(cfg.num_reels)), "Lapis FR0 wrong"
    pay_syms = {k[1] for k in cfg.paytable}
    assert "lapis" in pay_syms and "silver" not in pay_syms, "lapis paytable must rename silver"

    ca_cfg = ca.build_config()
    # For every cluster size, lapis's value == Candidate A's silver value.
    lapis_sizes = {k[0] for k in cfg.paytable if k[1] == "lapis"}
    for size in lapis_sizes:
        assert cfg.paytable[(size, "lapis")] == ca_cfg.paytable[(size, "silver")], (
            f"lapis pay at size {size} != Candidate A silver pay"
        )
    # Every other symbol's pay values must be identical between lapis and Candidate A.
    for size in lapis_sizes:
        for sym in ("earth", "stone", "timber", "copper", "gold", "emerald", "diamond", "ingot"):
            assert cfg.paytable[(size, sym)] == ca_cfg.paytable[(size, sym)], (
                f"{sym} pay at size {size} differs between lapis and Candidate A"
            )
    GameConfig._instance = None
    _ = GameConfig()
    print("  [ok] Lapis config reproducible + rename-neutral vs Candidate A")

    # 4. The baseline config must still reproduce its own strips (unchanged).
    assert sha256_strip(build_strip(20261117, BASE_COUNTS)) == BASE_SHA, "baseline base SHA changed"
    assert sha256_strip(build_strip(20261118, FREE_COUNTS)) == FREE_SHA, "baseline free SHA changed"
    print("  [ok] baseline strips unchanged after Lapis config build")


# ---------------------------------------------------------------------------
# 14. Variant P — persistent ore veins (DEV, separate config module)
# ---------------------------------------------------------------------------

def _variant_p_state(cap=None):
    """A state whose config is the Variant P config (persistent gate ON).

    The config singleton is reset so a fresh Variant P config is built; the
    caller must restore the baseline singleton/rule after use (see each test's
    `finally`). Returns (state, config).
    """
    from game_config import GameConfig
    import candidate_lapis_persistent_config as vp

    cfg = vp.build_config()
    if cap is not None:
        cfg.ore_vein_persist_max = cap
    state = GameState(cfg)
    state.betmode = "base"
    return state, cfg


def _restore_baseline():
    from game_config import GameConfig
    GameConfig._instance = None
    _ = GameConfig()


def test_variant_p_gate_default_off():
    """The `ore_vein_persist_freespins` gate DEFAULTS OFF.

    The baseline `game_config.py` must not enable the persistent mechanic, so
    every existing config (and the §3.1 game) behaves exactly as before. With
    the gate off, `persistent_veins` stays empty and no injection occurs.
    """
    config = GameConfig()
    assert config.ore_vein_persist_freespins is False, "baseline gate must default OFF"
    state = GameState(config)
    state.betmode = "base"
    state.criteria = "freegame"
    state.reset_book()
    state.gametype = config.freegame_type
    # A freegame board drawn with the gate off must not populate persistent_veins.
    state.draw_board(emit_event=False)
    assert state.persistent_veins == set(), f"persistent_veins not empty: {state.persistent_veins}"
    print("  [ok] Variant P gate defaults OFF; persistent_veins stays empty")
    _restore_baseline()


def test_variant_p_rescan_records_veins():
    """`_rescan_persistent_veins` records every ore vein on a freegame board."""
    state, cfg = _variant_p_state(cap=4)
    try:
        state.reset_book()
        state.gametype = cfg.freegame_type
        grid = [
            ["earth", "earth", "earth", "earth", "earth"],
            ["ore_vein", "stone", "timber", "copper", "lapis"],
            ["timber", "copper", "ore_vein", "copper", "timber"],
            ["copper", "timber", "copper", "timber", "copper"],
            ["timber", "copper", "timber", "copper", "timber"],
            ["copper", "timber", "copper", "timber", "copper"],
        ]
        state.board = [[state.create_symbol(name) for name in reel] for reel in grid]
        state.get_special_symbols_on_board()
        state._rescan_persistent_veins()
        assert (1, 0) in state.persistent_veins, f"vein at (1,0) not recorded: {state.persistent_veins}"
        assert (2, 2) in state.persistent_veins, f"vein at (2,2) not recorded: {state.persistent_veins}"
        # Only ore veins are recorded.
        assert all(state.board[r][c].name == "ore_vein" for (r, c) in state.persistent_veins), (
            "persistent_veins contains a non-vein position"
        )
        print("  [ok] rescan records ore-vein positions on the board")
    finally:
        _restore_baseline()


def test_variant_p_cap_bounds_set():
    """`ore_vein_persist_max` caps the number of persistent veins."""
    state, cfg = _variant_p_state(cap=2)
    try:
        state.reset_book()
        state.gametype = cfg.freegame_type
        grid = [
            ["earth", "earth", "earth", "earth", "earth"],
            ["ore_vein", "stone", "timber", "copper", "lapis"],
            ["timber", "copper", "ore_vein", "copper", "timber"],
            ["copper", "timber", "copper", "timber", "copper"],
            ["timber", "copper", "timber", "copper", "timber"],
            ["copper", "timber", "ore_vein", "timber", "copper"],
        ]
        state.board = [[state.create_symbol(name) for name in reel] for reel in grid]
        state.get_special_symbols_on_board()
        state._rescan_persistent_veins()
        assert len(state.persistent_veins) <= 2, f"cap=2 not honoured: {state.persistent_veins}"
        print(f"  [ok] persist cap bounds the set ({len(state.persistent_veins)} <= 2)")
    finally:
        _restore_baseline()


def test_variant_p_inject_places_veins():
    """`_inject_persistent_ore_veins` re-places the recorded veins at their
    recorded positions on a fresh freegame board."""
    state, cfg = _variant_p_state(cap=None)
    try:
        state.reset_book()
        state.gametype = cfg.freegame_type
        # Seed the persistent set with known positions.
        state.persistent_veins = {(1, 0), (3, 3)}
        # A fresh board with no ore veins (all common).
        grid = [
            ["earth", "earth", "earth", "earth", "earth"],
            ["stone", "stone", "stone", "stone", "stone"],
            ["timber", "timber", "timber", "timber", "timber"],
            ["copper", "copper", "copper", "copper", "copper"],
            ["earth", "earth", "earth", "earth", "earth"],
            ["stone", "stone", "stone", "stone", "stone"],
        ]
        state.board = [[state.create_symbol(name) for name in reel] for reel in grid]
        state.get_special_symbols_on_board()
        state._inject_persistent_ore_veins()
        assert state.board[1][0].name == "ore_vein", "vein not injected at (1,0)"
        assert state.board[3][3].name == "ore_vein", "vein not injected at (3,3)"
        # Injection also rescans, so the injected veins are recorded.
        assert (1, 0) in state.persistent_veins and (3, 3) in state.persistent_veins
        print("  [ok] persistent veins re-injected at their recorded positions")
    finally:
        _restore_baseline()


def test_variant_p_vein_explodes_but_position_persists():
    """A persistent vein that explodes is removed from the board, but its
    recorded position stays in `persistent_veins` for re-injection next spin."""
    state, cfg = _variant_p_state(cap=None)
    try:
        state.reset_book()
        state.gametype = cfg.freegame_type
        grid = [
            ["earth", "earth", "earth", "earth", "earth"],
            ["ore_vein", "stone", "timber", "copper", "lapis"],
            ["timber", "copper", "timber", "copper", "timber"],
            ["copper", "timber", "copper", "timber", "copper"],
            ["timber", "copper", "timber", "copper", "timber"],
            ["copper", "timber", "copper", "timber", "copper"],
        ]
        state.board = [[state.create_symbol(name) for name in reel] for reel in grid]
        state.get_special_symbols_on_board()
        state._rescan_persistent_veins()
        assert (1, 0) in state.persistent_veins, "vein not recorded"
        # Simulate the vein exploding: it is removed from the board (cell filled
        # with a new symbol) but its recorded position must be retained.
        state.board[1][0] = state.create_symbol("stone")
        state._rescan_persistent_veins()
        assert (1, 0) in state.persistent_veins, (
            f"exploded vein position lost: {state.persistent_veins}"
        )
        # The position is retained so the next free spin re-injects it.
        print("  [ok] exploded vein position retained for re-injection")
    finally:
        _restore_baseline()


def test_variant_p_config_reproducible():
    """The Variant P config is reproducible and matches its spec.

    - It uses the Lapis Lazuli strips (identical counts, seeds and SHAs).
    - The paytable is the merged 5-tier table (VARIANT_PAY_RANGES has 5 entries)
      with the common symbols baked at the calibration common-scale ~1.10; the
      5-7 cluster pays are all >= 0.10x.
    - The persistent-ore-vein gate is ON (config.ore_vein_persist_freespins).
    - The baseline `game_config.py` strips/SHAs stay byte-identical.
    """
    import candidate_lapis_config as lc
    import candidate_lapis_persistent_config as vp
    from game_config import GameConfig, build_strip, sha256_strip, BASE_COUNTS, FREE_COUNTS

    # 1. Strips are deterministic, length 200, counts + SHAs identical to Lapis.
    base, free = vp.build_lapis_strips()
    assert len(base) == 200 and len(free) == 200, "Variant P strips must be length 200"
    for sym, c in vp.BASE_COUNTS.items():
        assert base.count(sym) == c, f"Variant P base {sym} count {base.count(sym)} != {c}"
    for sym, c in vp.FREE_COUNTS.items():
        assert free.count(sym) == c, f"Variant P free {sym} count {free.count(sym)} != {c}"
    bs, fs = vp.sha256()
    assert bs == vp.BASE_SHA, f"Variant P base SHA mismatch {bs}"
    assert fs == vp.FREE_SHA, f"Variant P free SHA mismatch {fs}"
    assert vp.build_lapis_strips()[0] == base, "Variant P base strip not deterministic"
    assert vp.build_lapis_strips()[1] == free, "Variant P free strip not deterministic"

    # 2. Strips are byte-identical to the Lapis Lazuli strips.
    lbase, lfree = lc.build_lapis_strips()
    assert base == lbase, "Variant P base strip != Lapis base strip"
    assert free == lfree, "Variant P free strip != Lapis free strip"
    assert vp.BASE_SHA == lc.BASE_SHA, "Variant P base SHA != Lapis base SHA"
    assert vp.FREE_SHA == lc.FREE_SHA, "Variant P free SHA != Lapis free SHA"
    assert "silver" not in base and "silver" not in free, "silver must be fully removed"

    # 3. Merged 5-tier structure: VARIANT_PAY_RANGES has 5 ascending ranges.
    assert len(vp.VARIANT_PAY_RANGES) == 5, "must be a 5-tier merged paytable"
    assert vp.VARIANT_PAY_RANGES == [(5, 7), (8, 10), (11, 14), (15, 19), (20, 30)]
    for (lo, hi) in vp.VARIANT_PAY_RANGES:
        assert lo <= hi, "ranges must be ascending"

    # 4. build_config: gate ON, rule/target set, reels = lapis strips.
    cfg = vp.build_config()
    assert cfg.ore_vein_persist_freespins is True, "persistent gate must be ON"
    assert cfg.ore_vein_rule == "create-cluster", "ore-vein rule not set"
    assert cfg.ore_vein_target == "diamond", "ore-vein target not set"
    assert all(cfg.reels["BR0"][0] == base for _ in range(cfg.num_reels)), "Variant P BR0 wrong"
    assert all(cfg.reels["FR0"][0] == free for _ in range(cfg.num_reels)), "Variant P FR0 wrong"

    # 5. Every merged range maps to a single consistent value across its sizes.
    for (lo, hi) in vp.VARIANT_PAY_RANGES:
        for sym in ("earth", "stone", "timber", "copper", "lapis", "gold",
                    "emerald", "diamond", "ingot"):
            v0 = cfg.paytable[(lo, sym)]
            for sz in range(lo, hi + 1):
                assert cfg.paytable[(sz, sym)] == v0, (
                    f"{sym} pay not constant across merged range {lo}-{hi}"
                )

    # 6. All 5-7 cluster pays are >= 0.10x.
    for sym in ("earth", "stone", "timber", "copper", "lapis", "gold",
                "emerald", "diamond", "ingot"):
        assert cfg.paytable[(5, sym)] >= 0.10, f"{sym} 5-7 pay < 0.10x"

    # 7. Common symbols are baked at the calibration common-scale ~1.10 relative
    #    to the Lapis low-end merged values; premium/ingot are unscaled.
    lcfg = lc.build_config()
    for sym, vals in vp._P_COMMON_PAYS.items():
        for i, (lo, hi) in enumerate(vp.VARIANT_PAY_RANGES):
            lapis_merged = lcfg.paytable[(lo, sym)]
            assert vals[i] == round(lapis_merged * 1.10, 2), (
                f"{sym} merged pay {vals[i]} != round(lapis*1.10,2)={round(lapis_merged*1.10,2)}"
            )
    for sym, vals in vp._P_PREMIUM_PAYS.items():
        for i, (lo, hi) in enumerate(vp.VARIANT_PAY_RANGES):
            assert vals[i] == lcfg.paytable[(lo, sym)], (
                f"{sym} premium pay {vals[i]} != lapis {lo}-cluster pay"
            )
    for sym, vals in vp._P_INGOT_PAYS.items():
        for i, (lo, hi) in enumerate(vp.VARIANT_PAY_RANGES):
            assert vals[i] == lcfg.paytable[(lo, sym)], (
                f"{sym} ingot pay {vals[i]} != lapis {lo}-cluster pay"
            )

    GameConfig._instance = None
    _ = GameConfig()

    # 8. The baseline config must still reproduce its own strips (unchanged).
    assert sha256_strip(build_strip(20261117, BASE_COUNTS)) == BASE_SHA, "baseline base SHA changed"
    assert sha256_strip(build_strip(20261118, FREE_COUNTS)) == FREE_SHA, "baseline free SHA changed"
    print("  [ok] Variant P config reproducible + merged 5-tier + gate ON + "
          "strips == Lapis SHAs")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    tests = [
        test_strip_shas,
        test_book_invariants,
        test_win_event_sequence,
        test_tumble_between_wins,
        test_ore_vein_upgrade_with_target,
        test_ore_vein_upgrade_no_target,
        test_three_pickaxe_trigger,
        test_natural_trigger,
        test_retrigger_clamp,
        test_wincap,
        test_wincap_ore_vein_upgrade,
        test_create_cluster_rule_converts_when_paying_cluster,
        test_create_cluster_rule_no_convert_without_cluster,
        test_ore_vein_rule_dispatch,
        test_variant_config_reproducible,
        test_candidate2_config_reproducible,
        test_candidate_a_config_reproducible,
        test_candidate_b_config_reproducible,
        test_lapis_config_reproducible,
        test_variant_p_gate_default_off,
        test_variant_p_rescan_records_veins,
        test_variant_p_cap_bounds_set,
        test_variant_p_inject_places_veins,
        test_variant_p_vein_explodes_but_position_persists,
        test_variant_p_config_reproducible,
    ]
    failures = 0
    for t in tests:
        name = t.__name__
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"  [FAIL] {name}: {type(exc).__name__}: {exc}")
        else:
            print(f"  [PASS] {name}")
    print(f"\n{len(tests) - failures}/{len(tests)} tests passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
