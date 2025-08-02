import networkx as nx
import geopandas as gpd

from libadalina.graph.graph_factory import DEFAULT_EPSG
from libadalina.writers.to_csv import graph_to_pandas


def graph_to_shapefile(graph: nx.Graph, path: str):
    """
    Write a networkx graph to a shapefile.
    :param graph: The networkx graph to write.
    :param path: The path to the shapefile.
    """
    df = graph_to_pandas(graph)
    gdf_edges = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG)
    gdf_edges.to_file(path, driver='ESRI Shapefile')