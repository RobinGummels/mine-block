from src.executables.executables import Executables
from src.calculations.cluster import Cluster


class GameCalculations(Executables):
    """Block Cave cluster evaluation.

    The design (§5.4/§5.5) scores each cluster at its original size and marks
    the winning cells `explode=True`. There are no grid-position multipliers in
    Block Cave (unlike 0_0_cluster), so we reuse the engine's
    `Cluster.evaluate_clusters` and record the winning positions in
    `self.win_data` for the ore-vein upgrade step.
    """

    def get_clusters_update_wins(self):
        """Find clusters on the board and update the win manager."""
        clusters = Cluster.get_clusters(self.board, "wild")
        return_data = {"totalWin": 0, "wins": []}
        self.board, self.win_data, total_win = Cluster.evaluate_clusters(
            config=self.config,
            board=self.board,
            clusters=clusters,
            global_multiplier=self.global_multiplier,
            return_data=return_data,
        )
        self.win_data["totalWin"] += total_win

        Cluster.record_cluster_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data["totalWin"]
