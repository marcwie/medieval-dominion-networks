from __future__ import annotations

from collections.abc import Iterable
from os import PathLike

import numpy as np
import networkx as nx
import pandas as pd
from numpy.typing import NDArray

from .network import Network


class TemporalNetwork(Network):
    """Represent the co-dominion network as a sequence of yearly graphs."""

    def __init__(
        self,
        nodes_file: str | PathLike[str],
        edges_file: str | PathLike[str],
        edge_filter: str | None = None,
    ) -> None:
        """Load the data and construct yearly graphs and change statistics.

        Args:
            nodes_file: Path to the node CSV file.
            edges_file: Path to the edge CSV file.
            edge_filter: Party identifier to exclude, if any.
        """

        print('Initalizing temporal network...')
        super().__init__(edges_file=edges_file, nodes_file=nodes_file, edge_filter=edge_filter)

        self._years: NDArray[np.int64] = np.sort(self._edges.Year.unique())
        self._places: NDArray[np.int64] = self._nodes.PlaceID.unique()

        self.construct_networks()
        self.compute_hamming_distance()

    def construct_networks(self) -> None:
        """Build an undirected graph for each year in the edge data."""

        print('Constructing networks...')
        self._networks: dict[
            np.int64, nx.Graph[int, dict[str, object], dict[str, object]]
        ] = {}

        for year in self._years:
            edges = self._edges[self._edges.Year == year]
            edges = edges[['from', 'to']].values.tolist()
            G = nx.Graph()
            G.add_nodes_from(self._places)
            G.add_edges_from(edges)
            self._networks[year] = G

    def compute_hamming_distance(self) -> None:
        """Compute yearly changes in adjacency matrices between consecutive years."""

        print('Computing hamming distance...')
        self._hamming_distance: NDArray[np.float64] = np.zeros(len(self._years))
        self._hamming_distance[0] = np.nan

        for i, year in enumerate(self._years[1:]):
            A1 = nx.adjacency_matrix(self.G(year))
            A2 = nx.adjacency_matrix(self.G(year - 1))
            self._hamming_distance[i+1] = np.abs(A1 - A2).sum()

    def average_degree_sequence(self) -> NDArray[np.float64]:
        """Return the average degree for each year.

        Returns:
            An array of average degree values in the order returned by `years`.
        """

        average_degree: NDArray[np.float64] = np.zeros(len(self._years))

        for i, year in enumerate(self._years):
            average_degree[i] = self.G(year).number_of_edges() / self.G(year).number_of_nodes()

        return average_degree


    def get_city_names(self, node_list: Iterable[int] = []) -> pd.DataFrame:
        """Return unique identifiers and names for the requested cities.

        Args:
            node_list: Place identifiers to look up.

        Returns:
            A dataframe with `PlaceID` and `PlaceName` columns.
        """

        return self._nodes[self._nodes.PlaceID.isin(node_list)][['PlaceID', 'PlaceName']].drop_duplicates().reset_index(drop=True)


    def G(
        self, year: int | np.int64
    ) -> nx.Graph[int, dict[str, object], dict[str, object]]:
        """Return the graph for a year.

        Args:
            year: Year whose graph to retrieve.

        Returns:
            The undirected graph for that year.
        """
        return self._networks[year]

    def years(self) -> NDArray[np.int64]:
        """Return the years represented in the temporal network."""
        return self._years

    def hamming_distance(self) -> NDArray[np.float64]:
        """Return the adjacency-matrix change statistic for each year."""
        return self._hamming_distance