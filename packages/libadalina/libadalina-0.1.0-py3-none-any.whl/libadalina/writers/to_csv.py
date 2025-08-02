import networkx as nx
import pandas as pd
import geopandas as gpd

from libadalina.graph.graph_factory import DEFAULT_EPSG


def graph_to_pandas(graph: nx.Graph) -> pd.DataFrame:
    """
    Convert a networkx graph to a pandas DataFrame.
    :param graph: The networkx graph to convert.
    :return: A pandas DataFrame containing the edges of the graph.
    """
    return pd.DataFrame(({'from': u, 'to': v, **data} for u, v, data in graph.edges(data=True)))

def graph_to_csv(graph: nx.Graph, path: str):
    """
    Write a networkx graph to a CSV.
    :param graph: The networkx graph to write.
    :param path: The path to the CSV.
    """
    df = graph_to_pandas(graph)
    df.to_csv(path, index=False)

def path_to_pandas(graph: nx.Graph, path: list) -> pd.DataFrame:
    edges = [dict(_from= path[i], _to=path[i + 1], **graph.get_edge_data(path[i], path[i + 1])) for i in range(len(path) - 1)]
    return pd.DataFrame(edges)

def path_to_csv(graph: nx.Graph, path: list, file_path: str):
    df = path_to_pandas(graph, path)
    gdf_edges = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG)
    gdf_edges.to_csv(file_path, index=False)  # Save as CSV