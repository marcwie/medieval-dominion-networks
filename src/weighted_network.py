from __future__ import annotations

from collections.abc import Sequence
from os import PathLike

import networkx as nx

from .network import Network

class WeightedNetwork(Network):
    """Represent pooled co-dominion ties as edges weighted by frequency."""

    def __init__(
        self,
        nodes_file: str | PathLike[str],
        edges_file: str | PathLike[str],
        year0: int | None = None,
        year1: int | None = None,
        edge_filter: str | None = None,
    ) -> None:
        """Load and construct the pooled network, optionally within a year range.

        Args:
            nodes_file: Path to the node CSV file.
            edges_file: Path to the edge CSV file.
            year0: Optional inclusive first year.
            year1: Optional inclusive last year.
            edge_filter: Party identifier to exclude, if any.
        """

        print('Initializing weighted network...')
        super().__init__(nodes_file=nodes_file, edges_file=edges_file, edge_filter=edge_filter)

        if year0 is None and year1 is None:
            print('No time frame specified. Using full data.')

        self._year0 = year0
        self._year1 = year1
        self._comms: Sequence[set[int]] | None = None

        self._select_timeframe()

        self.construct_network()

    def _select_timeframe(self) -> None:
        """Restrict the edge data to the configured inclusive year range."""

        if self._year0:
            self._edges = self._edges[self._edges.Year >= self._year0]

        if self._year1:
            self._edges = self._edges[self._edges.Year <= self._year1]


    def construct_network(self, normalize: bool = True) -> None:
        """Build the pooled graph with edge weights based on the number of years.

        Args:
            normalize: If true, scale weights so the largest is one.
        """

        edge_weights = self._edges.groupby(['from', 'to']).Year.count().reset_index().rename(columns={'Year': 'weight'})

        if normalize:
            edge_weights.weight /= edge_weights.weight.max()

        edge_weights = edge_weights.values.tolist()
        edge_weights = [[int(e[0]), int(e[1]), e[2]] for e in edge_weights]

        G = nx.Graph()
        G.add_weighted_edges_from(edge_weights)

        self._G: nx.Graph[int, dict[str, object], dict[str, object]] = G


    def compute_communities(self, max_communities: int = 10, seed: int = 0) -> None:
        """Detect communities and retain the largest requested groups.

        Args:
            max_communities: Maximum number of communities to keep.
            seed: Random seed for Louvain community detection.
        """

        comms = nx.community.louvain_communities(self._G, seed=seed)
        comms = sorted(comms, key=len, reverse=True)[:max_communities]

        self._comms = comms


    def set_communities(self, communities: Sequence[set[int]]) -> None:
        """Set the communities used by this network.

        Args:
            communities: Sequence of node groups to store as communities.
        """

        self._comms = communities

    def G(self) -> nx.Graph[int, dict[str, object], dict[str, object]]:
        """Return the pooled weighted graph."""

        return self._G

    def communities(self) -> Sequence[set[int]]:
        """Return the stored communities, detecting them if not yet available.

        Returns:
            Communities ordered from largest to smallest.
        """

        if not self._comms:
            self.compute_communities()

        assert self._comms is not None
        return self._comms