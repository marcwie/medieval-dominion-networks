import pandas as pd
import networkx as nx
import numpy as np


class WeightedNetwork():

    def __init__(self, nodes_file, edges_file):

        self._nodes = pd.read_csv(nodes_file)
        self._edges = pd.read_csv(edges_file)
        self._edges['ruling_party_category'] = self._edges.PartyID.str[0]

        self._position = self._nodes[['PlaceID', 'XCOORD', 'YCOORD']].drop_duplicates().set_index('PlaceID').to_dict('index')
        self._position = {key: (value['XCOORD'], value['YCOORD']) for key, value in self._position.items()}

        self.construct_network()
        self.compute_communities()


    def construct_network(self, normalize=True):

        edge_weights = self._edges.groupby(['from', 'to']).Year.count().reset_index().rename(columns={'Year': 'weight'})

        if normalize:
            edge_weights.weight /= edge_weights.weight.max()

        edge_weights = edge_weights.values.tolist()
        edge_weights = [[int(e[0]), int(e[1]), e[2]] for e in edge_weights]

        G = nx.Graph()
        G.add_weighted_edges_from(edge_weights)

        self._G = G


    def compute_communities(self, max_communities=10, seed=0):

        comms = nx.community.louvain_communities(self._G, seed=seed)
        T = np.sort([len(c) for c in comms])[-max_communities]
        comms = [c for c in comms if len(c) >= T]
        assert len(comms) <= max_communities

        self._comms = comms


    def nodes(self):

        return self._nodes

    def edges(self):

        return self._edges

    def position(self):

        return self._position

    def G(self):

        return self._G

    def communities(self):

        return self._comms