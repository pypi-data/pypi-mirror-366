import networkx as nx
import geopandas as gpd
import pandas as pd
import pyspark.sql as ps
from libadalina.graph.constants import DEFAULT_EPSG
from libadalina.writers.to_csv import graph_to_pandas, path_to_pandas


def dataframe_to_geopackage(df: pd.DataFrame | gpd.GeoDataFrame | ps.DataFrame, path: str):
    if isinstance(df, ps.DataFrame):
        df = gpd.GeoDataFrame(df.toPandas(), geometry = 'geometry', crs = DEFAULT_EPSG)
    elif isinstance(df,  pd.DataFrame):
        df = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG)
    elif isinstance(df, gpd.GeoDataFrame):
        pass # already a GeoDataFrame
    else:
        raise TypeError(f"Unsupported type {type(df)}. Expected pd.DataFrame, gpd.GeoDataFrame, or ps.DataFrame.")
    df.to_file(path, layer='dataframe', driver="GPKG")


def graph_to_geopackage(graph: nx.Graph, path: str):
    """
    Write a networkx graph to a geopackage.
    :param graph: The networkx graph to write.
    :param path: The path to the geopackage.
    """
    df = graph_to_pandas(graph)
    gdf_edges = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG)
    gdf_edges.to_file(path, driver='GPKG', layer='graph')


def path_to_geopackage(graph: nx.Graph, path: list, file_path: str):
    df = path_to_pandas(graph, path)
    gdf_edges = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG)
    gdf_edges.to_file(file_path, driver='GPKG', layer='path')