from .network import Network
import numpy as np
import networkx as nx


class TemporalNetwork(Network):

    def __init__(self, nodes_file, edges_file, edge_filter=None):
        super().__init__(edges_file=edges_file, nodes_file=nodes_file, edge_filter=edge_filter)

        self._years = np.sort(self._edges.Year.unique())
        self._places = self._nodes.PlaceID.unique()

        self.construct_networks()
        self.compute_hamming_distance()

    def construct_networks(self):

        print('Constructing networks...')
        self._networks = {}

        for year in self._years:
            edges = self._edges[self._edges.Year == year]
            edges = edges[['from', 'to']].values.tolist()
            G = nx.Graph()
            G.add_nodes_from(self._places)
            G.add_edges_from(edges)
            self._networks[year] = G

    def compute_hamming_distance(self):

        print('Computing hamming distance...')
        self._hamming_distance = np.zeros(len(self._years))
        self._hamming_distance[0] = np.nan

        for i, year in enumerate(self._years[1:]):
            A1 = nx.adjacency_matrix(self.G(year))
            A2 = nx.adjacency_matrix(self.G(year - 1))
            self._hamming_distance[i+1] = np.abs(A1 - A2).sum()

    def average_degree_sequence(self):

        average_degree = np.zeros(len(self._years))

        for i, year in enumerate(self._years):
            average_degree[i] = self.G(year).number_of_edges() / self.G(year).number_of_nodes()

        return average_degree


#    def collapse(self, year0, year1, aggregation='binarize'):
#
#        A = nx.adjacency_matrix(self.G(year0))
#        for year in range(year0, year1+1):
#            A += nx.adjacency_matrix(self.G(year))
#
#        if aggregation == 'binarize':
#            A = (A >= 1).astype(int)
#        elif aggregate == 'always':
#            A = (A == A.max()).astype(int)
#        elif aggregate == 'majority':
#            A = (A >= (0.5 * A.max())).astype(int)
#        else:
#            assert False
#
#        G = nx.Graph(A)
#        mapping = {i: place for i, place in enumerate(self._places)}
#        G = nx.relabel_nodes(G, mapping)
#
#        return G

    def get_city_names(self, node_list=[]):

        return self._nodes[self._nodes.PlaceID.isin(node_list)][['PlaceID', 'PlaceName']].drop_duplicates().reset_index(drop=True)


    def G(self, year):
        return self._networks[year]

    def years(self):
        return self._years

    def hamming_distance(self):
        return self._hamming_distance