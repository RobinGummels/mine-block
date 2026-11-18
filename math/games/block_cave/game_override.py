from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import reveal_event, fs_trigger_event


class GameStateOverride(GameExecutables):
    """Overrides the universal state functions for Block Cave.

    The key changes implement the design's natural free-spin triggering
    (MATH_DESIGN.md §6.2a): the base-game threshold re-draw suppression is
    removed, and scatter counting is evaluated against the INITIAL board of
    each spin (no accumulation across tumbles, §6.1/§6.2).

    Variant P (persistent ore veins): when `config.ore_vein_persist_freespins`
    is True (set only by a DEV variant config; defaults OFF), ore veins persist
    across a free-spin series. Every ore vein that lands on a free-spin board is
    recorded as persistent, and its position carries forward to subsequent free
    spins in the same series (re-injected before each free-spin reveal). The
    persistent veins are NOT locked: during a cascade they behave like normal
    ore veins and can explode. This breaks the positive feedback that a locked,
    never-exploding vein creates (a wild that never leaves the board feeds the
    cascade and lands new veins that also never leave, saturating the board and
    running to the 1000x cap). The whole series is a single book;
    `persistent_veins` is reset at series start so no state transfers to a later
    paid round. There is no bonus multiplier in Variant P.
    """

    def reset_book(self):
        super().reset_book()
        self.initial_scatter_count = 0
        self.initial_scatter_positions = []
        self.persistent_veins = set()

    def reset_fs_spin(self):
        super().reset_fs_spin()
        self.persistent_veins = set()

    def assign_special_sym_function(self):
        pass

    def _persist_enabled(self) -> bool:
        """True when the Variant P persistent-ore-vein gate is on."""
        return bool(getattr(self.config, "ore_vein_persist_freespins", False))

    def _rescan_persistent_veins(self) -> None:
        """Rebuild `persistent_veins` from every ore vein currently on the board.

        Called after the board is drawn (with injected veins) and after every
        tumble, because a tumble shifts cell positions and may land new ore
        veins. Every ore vein on a free-spin board becomes persistent, up to
        `config.ore_vein_persist_max` (if set) so the set cannot grow without
        bound.

        Unlike the earlier prototype, persistent veins are NOT locked: they
        behave like normal ore veins during a cascade (they can be part of a
        winning cluster and explode). Locking them caused a positive feedback
        loop (a vein feeds the cascade, never leaves, and the cascade lands new
        veins that also never leave) that saturated the board and ran to the
        1000x cap. The persistence here is positional: the recorded positions
        are re-injected at the start of the NEXT free spin, so a vein that
        explodes regenerates at its recorded position. The set is therefore
        capped so it cannot grow across a long series.
        """
        cap = getattr(self.config, "ore_vein_persist_max", None)
        # Keep veins already recorded as persistent (they carried in), then add
        # newly-drawn veins up to the cap.
        new_set = set(self.persistent_veins)
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                if self.board[reel][row].name == "ore_vein":
                    new_set.add((reel, row))
        if cap is not None and len(new_set) > cap:
            # Keep the existing persistent veins first; add new ones in scan
            # order only until the cap is reached.
            kept = [p for p in self.persistent_veins if p in new_set]
            rest = [p for p in new_set if p not in kept]
            new_set = set(kept[:cap])
            for p in rest:
                if len(new_set) >= cap:
                    break
                new_set.add(p)
        self.persistent_veins = new_set

    def _inject_persistent_ore_veins(self) -> None:
        """Inject the persistent veins at their recorded positions.

        Runs only for a freegame board, after the board is drawn and before the
        reveal event, so the reveal and every subsequent cluster evaluation see
        the persistent wilds. After injection the special symbols and the
        anticipation are recomputed (a vein may have overwritten a scatter), and
        the board is rescanned so every ore vein becomes persistent.
        """
        for (reel, row) in self.persistent_veins:
            if 0 <= reel < self.config.num_reels and 0 <= row < self.config.num_rows[reel]:
                self.board[reel][row] = self.create_symbol("ore_vein")
        self.get_special_symbols_on_board()
        self._recompute_anticipation()
        self._rescan_persistent_veins()

    def _recompute_anticipation(self) -> None:
        """Recompute the reveal anticipation from the current scatter positions.

        Mirrors the logic in `create_board_reelstrips` (anticipation counts up
        from the first reel containing a scatter). Called after persistent-vein
        injection, which may have overwritten a scatter.
        """
        first_scatter_reel = -1
        for reel in range(self.config.num_reels):
            if any(p["reel"] == reel for p in self.special_syms_on_board["scatter"]):
                first_scatter_reel = reel
                break
        anticipation = [0] * self.config.num_reels
        if first_scatter_reel > -1:
            count = 1
            for reel in range(first_scatter_reel, self.config.num_reels):
                anticipation[reel] = count
                count += 1
        self.anticipation = anticipation

    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Draw the initial board.

        The base-game threshold re-draw suppression loop is removed so a board
        with 3+ pickaxes can trigger free spins naturally. The forced-freegame
        branch is preserved for criteria that require a specific scatter count
        (e.g. `scatter_triggers`). For a freegame board with Variant P enabled,
        persistent ore veins are injected before the reveal.
        """
        if (
            self.get_current_distribution_conditions()["force_freegame"]
            and self.gametype == self.config.basegame_type
        ):
            num_scatters = get_random_outcome(self.get_current_distribution_conditions()["scatter_triggers"])
            self.force_special_board(trigger_symbol, num_scatters)
        else:
            self.create_board_reelstrips()
        if self._persist_enabled() and self.gametype == self.config.freegame_type:
            self._inject_persistent_ore_veins()
        if emit_event:
            reveal_event(self)

    def tumble_board(self) -> None:
        """Perform the tumble, then rescan the persistent-vein positions.

        Persistent veins are NOT locked: they behave like normal ore veins
        during a cascade, so they can be part of a winning cluster and explode
        (removed by the parent tumble). After the parent tumble (which shifts
        cell positions and may land new ore veins), the board is rescanned so
        `persistent_veins` stays current. A vein that explodes is removed from
        the board but its recorded position remains in `persistent_veins`, so it
        is re-injected at the start of the next free spin.
        """
        super().tumble_board()
        if self._persist_enabled() and self.gametype == self.config.freegame_type:
            self._rescan_persistent_veins()

    def check_fs_condition(self, scatter_key: str = "scatter") -> bool:
        """A trigger requires the INITIAL-board scatter count to reach the
        threshold. Pickaxes that tumble in later do not count (§6.1/§6.2)."""
        return (
            self.initial_scatter_count >= min(self.config.freespin_triggers[self.gametype].keys())
            and not self.repeat
        )

    def check_freespin_entry(self, scatter_key: str = "scatter") -> bool:
        """Allow a natural trigger even when `force_freegame` is False.

        Logic: if the initial scatter count reaches the threshold, return True
        (natural trigger allowed). Otherwise, if `force_freegame` is True, set
        `self.repeat = True` (the spin must be re-drawn) and return False.
        Otherwise return False.
        """
        if self.initial_scatter_count >= min(self.config.freespin_triggers[self.gametype].keys()):
            return True
        if self.get_current_distribution_conditions()["force_freegame"]:
            self.repeat = True
            return False
        return False

    def run_freespin_from_base(self, scatter_key: str = "scatter") -> None:
        """Trigger the freespin function using the initial scatter count."""
        self.record(
            {
                "kind": self.initial_scatter_count,
                "symbol": scatter_key,
                "gametype": self.gametype,
            }
        )
        self.update_freespin_amount()
        self.run_freespin()

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Set the initial number of spins, clamping the pickaxe count to 6 (§6.3)."""
        count = min(self.initial_scatter_count, 6)
        self.tot_fs = self.config.freespin_triggers[self.gametype][count]
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        self._emit_trigger_with_initial_positions(basegame_trigger, freegame_trigger, scatter_key)

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """Add retrigger spins, clamping the count to 6 and the total to 60 (§6.4)."""
        count = min(self.initial_scatter_count, 6)
        self.tot_fs += self.config.freespin_triggers[self.gametype][count]
        self.tot_fs = min(self.tot_fs, 60)
        self._emit_trigger_with_initial_positions(False, True, scatter_key)

    def _emit_trigger_with_initial_positions(self, basegame_trigger, freegame_trigger, scatter_key):
        """Emit the free-spin trigger using the initial scatter positions, so the
        event reflects the triggering board rather than the post-tumble board."""
        saved = self.special_syms_on_board[scatter_key]
        self.special_syms_on_board[scatter_key] = [dict(p) for p in self.initial_scatter_positions]
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)
        self.special_syms_on_board[scatter_key] = saved

    def check_repeat(self) -> None:
        """Checks if the spin failed a criteria constraint at any point.

        Block Cave does NOT force a non-zero win for non-"0" criteria (the
        cluster game's `running_bet_win == 0 and criteria != "0"` rule is a
        calibration tool, not a Block Cave rule). Only a win_criteria mismatch
        or an unmet `force_freegame` causes a repeat.
        """
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if self.get_current_distribution_conditions()["force_freegame"] and not self.triggered_freegame:
                self.repeat = True

        self.repeat_count += 1
        self.check_current_repeat_count()
