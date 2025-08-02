import networkx as nx
from matplotlib import pyplot as plt

def get_node_of_address(graph, address):
    """
    Get the node of a given address in the graph.

    :param graph: The networkx graph.
    :param address: The address to search for.
    :return: The node ID if found, otherwise None.
    """
    for u, v, data in graph.edges(data=True):
        if address.lower() in data.get('name', '').lower():
            return u
    return None


def _draw_graph(graph: nx.Graph):
    edges = graph.edges(data=True)
    column_names = list(next(iter(edges))[2].keys())
    edges_data = [edge[2] for edge in edges]
    positions = {node: (data['geometry'].x, data['geometry'].y) for node, data in graph.nodes(data=True)}
    plt.figure(figsize=(100, 100), dpi=1200)
    nx.draw(graph, positions, node_size=1, arrowsize=2)
    # plt.show()
    plt.savefig("graph.pdf")
    # df = pd.DataFrame(edges_data, columns=column_names)
    # gdf = gpd.GeoDataFrame(df, geometry='geometry')
    # gdf.set_crs(epsg=DEFAULT_EPSG, inplace=True)
    # gdf.to_file("graph_geometries.gpkg", layer='graph', driver="GPKG")


nx.Graph.draw_adalina = _draw_graph