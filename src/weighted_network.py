import pandas as pd
import networkx as nx
import numpy as np
from .network import Network

class WeightedNetwork(Network):

    def __init__(self, nodes_file, edges_file, year0=None, year1=None, edge_filter=None):

        super().__init__(nodes_file=nodes_file, edges_file=edges_file, edge_filter=edge_filter)

        if year0 is None and year1 is None:
            print('No time frame specified. Using full data.')

        #if edge_filter is None:
        #    print('No edge filter specified. Using full data.')

        self._year0 = year0
        self._year1 = year1
        #self._edge_filter = edge_filter
        self._comms = None

        #self._nodes = pd.read_csv(nodes_file)
        #self._edges = pd.read_csv(edges_file)
        #self._edges['ruling_party_category'] = self._edges.PartyID.str[0]

        self._select_timeframe()
        #self._filter_edges()

        #self._position = self._nodes[['PlaceID', 'XCOORD', 'YCOORD']].drop_duplicates().set_index('PlaceID').to_dict('index')
        #self._position = {key: (value['XCOORD'], value['YCOORD']) for key, value in self._position.items()}

        self.construct_network()


    #def _filter_edges(self):
    #    self._edges = self._edges[self._edges.PartyID != self._edge_filter]


    def _select_timeframe(self):

        if self._year0:
            self._edges = self._edges[self._edges.Year >= self._year0]

        if self._year1:
            self._edges = self._edges[self._edges.Year <= self._year1]


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
        comms = sorted(comms, key=len, reverse=True)[:max_communities]

        self._comms = comms


    #def nodes(self):
    #    return self._nodes

    #def edges(self):
    #    return self._edges

    #def position(self):
    #    return self._position

    def G(self):

        return self._G

    def communities(self):

        if not self._comms:
            self.compute_communities()

        return self._comms