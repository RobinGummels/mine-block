"""Candidate ore-vein upgrade rules for the Stage 3 variant (DEV measurement only).

Each rule is a callable ``rule(state, target)`` that:

* reads ``state.board``, ``state.config`` and ``state.win_data``;
* mutates ``state.board`` (converts eligible regular blocks to ``target``);
* returns ``(vein_positions, upgrades)`` for the ``oreVeinUpgrade`` event,
  where rows are already padded (+1) per the event convention.

The ``baseline`` rule reproduces MATH_DESIGN.md §5.3 exactly (convert the first
eligible orthogonal neighbour of each activated vein). It is the default so the
validated §3.1 game is unchanged. The other rules are candidates for a
positive-RTP ore-vein contribution and are DEV-only.

Nothing here is a production claim.
"""

from __future__ import annotations

# Minimum cluster size that pays (MATH_DESIGN.md §3.1 PAY_RANGES start at (5,5)).
_MIN_PAY_CLUSTER = 5


def _winning_positions(state) -> set:
    """Return the set of (reel, row) that are members of a winning cluster."""
    w = set()
    for win in state.win_data["wins"]:
        for pos in win["positions"]:
            w.add((pos["reel"], pos["row"]))
    return w


def _eligible_neighbours(state, reel, row, target):
    """Yield eligible orthogonal neighbours in scan order (up, down, left, right)."""
    config = state.config
    for n_reel, n_row in (
        (reel, row - 1),
        (reel, row + 1),
        (reel - 1, row),
        (reel + 1, row),
    ):
        if n_reel < 0 or n_reel >= config.num_reels:
            continue
        if n_row < 0 or n_row >= config.num_rows[n_reel]:
            continue
        name = state.board[n_reel][n_row].name
        if name != "ore_vein" and name != "pickaxe" and name != target:
            yield (n_reel, n_row)


def _apply_upgrade(state, t_reel, t_row, target, winning, vein_positions, upgrades):
    """Convert a board cell to `target`, record it, and append to the lists."""
    state.board[t_reel][t_row] = state.create_symbol(target)
    if (t_reel, t_row) in winning:
        state.board[t_reel][t_row].explode = True
    upgrades.append({"reel": t_reel, "row": t_row + 1, "symbol": target})


def _cluster_size_if_converted(state, t_reel, t_row, target, winning):
    """Size of the paying target/wild cluster that converting (t_reel,t_row) to
    `target` would create, counting only cells that survive the tumble (not in
    `winning`). Ore_vein acts as a wild. Returns the cluster size (>=1) or 0 if
    the cell cannot survive the tumble (it is in the winning cluster)."""
    board = state.board
    config = state.config
    if (t_reel, t_row) in winning:
        return 0
    seen = set()
    stack = []
    # Seed the BFS from target/wild neighbours of the converted cell.
    for n_reel, n_row in (
        (t_reel, t_row - 1),
        (t_reel, t_row + 1),
        (t_reel - 1, t_row),
        (t_reel + 1, t_row),
    ):
        if n_reel < 0 or n_reel >= config.num_reels:
            continue
        if n_row < 0 or n_row >= config.num_rows[n_reel]:
            continue
        pos = (n_reel, n_row)
        if pos in seen or pos in winning:
            continue
        name = board[n_reel][n_row].name
        if name == target or name == "ore_vein":
            seen.add(pos)
            stack.append(pos)
    size = 1  # the converted cell itself
    while stack:
        reel, row = stack.pop()
        size += 1
        for n_reel, n_row in (
            (reel, row - 1),
            (reel, row + 1),
            (reel - 1, row),
            (reel + 1, row),
        ):
            if n_reel < 0 or n_reel >= config.num_reels:
                continue
            if n_row < 0 or n_row >= config.num_rows[n_reel]:
                continue
            pos = (n_reel, n_row)
            if pos in seen or pos in winning:
                continue
            name = board[n_reel][n_row].name
            if name == target or name == "ore_vein":
                seen.add(pos)
                stack.append(pos)
    return size


def _is_isolated(state, reel, row, winning):
    """True if (reel,row) has no same-symbol surviving orthogonal neighbour
    (i.e. converting it cannot break a would-be cluster)."""
    board = state.board
    config = state.config
    name = board[reel][row].name
    for n_reel, n_row in (
        (reel, row - 1),
        (reel, row + 1),
        (reel - 1, row),
        (reel + 1, row),
    ):
        if n_reel < 0 or n_reel >= config.num_reels:
            continue
        if n_row < 0 or n_row >= config.num_rows[n_reel]:
            continue
        if (n_reel, n_row) in winning:
            continue
        if board[n_reel][n_row].name == name:
            return False
    return True


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

def rule_baseline(state, target):
    """§5.3 baseline: convert the first eligible neighbour per activated vein."""
    winning = _winning_positions(state)
    vein_positions = []
    upgrades = []
    for reel in range(state.config.num_reels):
        for row in range(state.config.num_rows[reel]):
            cell = state.board[reel][row]
            if cell.name == "ore_vein" and (reel, row) in winning:
                vein_positions.append({"reel": reel, "row": row + 1})
                for t_reel, t_row in _eligible_neighbours(state, reel, row, target):
                    _apply_upgrade(state, t_reel, t_row, target, winning, vein_positions, upgrades)
                    break
    return vein_positions, upgrades


def rule_create_cluster(state, target):
    """Convert the first eligible neighbour ONLY IF it creates a paying target
    cluster (size >= 5) among surviving (non-winning) blocks.

    The converted cell must survive the tumble (out-of-cluster). This avoids
    wasting an upgrade on a cell that is removed, and avoids converting a cell
    that does not complete a paying cluster.
    """
    winning = _winning_positions(state)
    vein_positions = []
    upgrades = []
    for reel in range(state.config.num_reels):
        for row in range(state.config.num_rows[reel]):
            cell = state.board[reel][row]
            if cell.name == "ore_vein" and (reel, row) in winning:
                vein_positions.append({"reel": reel, "row": row + 1})
                for t_reel, t_row in _eligible_neighbours(state, reel, row, target):
                    if _cluster_size_if_converted(state, t_reel, t_row, target, winning) >= _MIN_PAY_CLUSTER:
                        _apply_upgrade(state, t_reel, t_row, target, winning, vein_positions, upgrades)
                        break
    return vein_positions, upgrades


def rule_isolated(state, target):
    """Convert the first eligible neighbour ONLY IF it is isolated (no same-symbol
    surviving neighbour) AND the conversion creates a paying target cluster.

    An isolated block contributes nothing to any cluster, so converting it has
    no downside; the only effect is the paying target cluster it may complete.
    """
    winning = _winning_positions(state)
    vein_positions = []
    upgrades = []
    for reel in range(state.config.num_reels):
        for row in range(state.config.num_rows[reel]):
            cell = state.board[reel][row]
            if cell.name == "ore_vein" and (reel, row) in winning:
                vein_positions.append({"reel": reel, "row": row + 1})
                for t_reel, t_row in _eligible_neighbours(state, reel, row, target):
                    if (t_reel, t_row) in winning:
                        continue
                    if not _is_isolated(state, t_reel, t_row, winning):
                        continue
                    if _cluster_size_if_converted(state, t_reel, t_row, target, winning) >= _MIN_PAY_CLUSTER:
                        _apply_upgrade(state, t_reel, t_row, target, winning, vein_positions, upgrades)
                        break
    return vein_positions, upgrades


def rule_convert_all(state, target):
    """Convert EVERY eligible surviving (out-of-cluster) neighbour of each
    activated vein to the target. This maximises the chance of forming a paying
    target cluster around the vein, at the cost of converting more cells."""
    winning = _winning_positions(state)
    vein_positions = []
    upgrades = []
    for reel in range(state.config.num_reels):
        for row in range(state.config.num_rows[reel]):
            cell = state.board[reel][row]
            if cell.name == "ore_vein" and (reel, row) in winning:
                vein_positions.append({"reel": reel, "row": row + 1})
                for t_reel, t_row in _eligible_neighbours(state, reel, row, target):
                    if (t_reel, t_row) in winning:
                        continue
                    _apply_upgrade(state, t_reel, t_row, target, winning, vein_positions, upgrades)
    return vein_positions, upgrades


def rule_out_of_cluster(state, target):
    """Convert the first eligible neighbour that SURVIVES the tumble (not in the
    winning cluster). Skips in-cluster cells whose conversion is wasted, but
    still converts out-of-cluster cells even if no paying cluster is created.
    """
    winning = _winning_positions(state)
    vein_positions = []
    upgrades = []
    for reel in range(state.config.num_reels):
        for row in range(state.config.num_rows[reel]):
            cell = state.board[reel][row]
            if cell.name == "ore_vein" and (reel, row) in winning:
                vein_positions.append({"reel": reel, "row": row + 1})
                for t_reel, t_row in _eligible_neighbours(state, reel, row, target):
                    if (t_reel, t_row) in winning:
                        continue
                    _apply_upgrade(state, t_reel, t_row, target, winning, vein_positions, upgrades)
                    break
    return vein_positions, upgrades


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_RULES = {
    "baseline": rule_baseline,
    "create-cluster": rule_create_cluster,
    "isolated": rule_isolated,
    "convert-all": rule_convert_all,
    "out-of-cluster": rule_out_of_cluster,
}


def get_rule(name):
    """Return the rule callable for `name` (defaults to baseline)."""
    return _RULES.get(name, rule_baseline)
