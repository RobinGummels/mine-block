"""Block Cave game-specific events."""

ORE_VEIN_UPGRADE = "oreVeinUpgrade"


def _clone(obj: object):
    t = type(obj)
    if t == dict:
        return {k: _clone(v) for k, v in obj.items()}
    elif t == list:
        return [_clone(x) for x in obj]
    return obj


def ore_vein_upgrade_event(gamestate, vein_positions, upgrades):
    """Emit the ore-vein upgrade event.

    Args:
        vein_positions: list of {"reel": int, "row": int} for every vein that
            activated in this cascade step (padded row convention).
        upgrades: list of {"reel": int, "row": int, "symbol": str} for every
            block actually converted (padded row convention). len(upgrades)
            may be <= len(vein_positions).
    """
    event = {
        "index": len(gamestate.book.events),
        "type": ORE_VEIN_UPGRADE,
        "veinPositions": _clone(vein_positions),
        "upgrades": _clone(upgrades),
    }
    gamestate.book.add_event(event)
