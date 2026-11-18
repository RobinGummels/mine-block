from game_calculations import GameCalculations
from src.events.events import update_freespin_event, win_info_event, update_tumble_win_event
from game_events import ore_vein_upgrade_event
from ore_vein_rules import get_rule


# The ore-vein upgrade target symbol is configurable (defaults to the §3.1
# baseline `diamond`). The target is read from `self.config.ore_vein_target`
# (default `"diamond"`), so the baseline game and any Stage-3 variant can share
# this code path without changing `game_config.py`.
_DEFAULT_ORE_TARGET = "diamond"


def _ore_target(config):
    return getattr(config, "ore_vein_target", _DEFAULT_ORE_TARGET)


class GameExecutables(GameCalculations):
    """Game dependent grouped functions."""

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.win_data = {}

    def emit_tumble_win_events(self) -> None:
        """Transmit win, tumble-win, wincap and ore-vein upgrade information.

        Emission order per cascade (MATH_DESIGN.md §8): `winInfo` ->
        `updateTumbleWin` -> [`wincap`] -> [`oreVeinUpgrade`] -> `tumbleBoard`.
        """
        if self.win_data["totalWin"] > 0:
            win_info_event(self)
            update_tumble_win_event(self)
            self.evaluate_wincap()
            self.process_ore_vein_upgrades()

    def process_ore_vein_upgrades(self):
        """Process ore-vein activations for the current cascade.

        A vein activates when it is a member of a winning cluster (its position
        is in `winning_positions`). The configured rule (`config.ore_vein_rule`,
        default ``"baseline"``) selects which eligible adjacent regular blocks
        are converted to the configured target symbol
        (`config.ore_vein_target`, default ``"diamond"``). The baseline rule
        converts at most one eligible neighbour per activated vein in scan
        order (MATH_DESIGN.md §5.3); candidate Stage-3 rules are DEV-only.

        Emits an `oreVeinUpgrade` event with padded row convention (row + 1).
        """
        if self.win_data["totalWin"] <= 0:
            return

        target = _ore_target(self.config)
        rule_name = getattr(self.config, "ore_vein_rule", "baseline")
        rule = get_rule(rule_name)
        vein_positions, upgrades = rule(self, target)

        if vein_positions:
            ore_vein_upgrade_event(self, vein_positions, upgrades)
