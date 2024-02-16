import pandas as pd


class Network():

    def __init__(self, nodes_file, edges_file, edge_filter=None):

        if edge_filter is None:
            print('No edge filter specified. Using full data.')

        self._nodes = pd.read_csv(nodes_file)
        self._position = self._nodes[['PlaceID', 'XCOORD', 'YCOORD']].drop_duplicates().set_index('PlaceID').to_dict('index')
        self._position = {key: (value['XCOORD'], value['YCOORD']) for key, value in self._position.items()}

        self._edge_filter = edge_filter
        self._edges = pd.read_csv(edges_file)
        self._edges['ruling_party_category'] = self._edges.PartyID.str[0]
        self._filter_edges()


    def _filter_edges(self):

        self._edges = self._edges[self._edges.PartyID != self._edge_filter]

    def nodes(self):

        return self._nodes

    def edges(self):

        return self._edges

    def position(self):

        return self._position