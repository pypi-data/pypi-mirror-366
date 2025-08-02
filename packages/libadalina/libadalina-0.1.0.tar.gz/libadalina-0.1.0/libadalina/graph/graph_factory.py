import dataclasses
from typing import Callable

import networkx as nx
import geopandas as gpd
import pandas as pd
import shapely
from pyspark.sql import DataFrame, Column
from sedona.sql import ST_Points, ST_Dump, ST_LineSegments, ST_Intersects, \
    ST_Buffer, ST_Intersection, ST_Area, ST_Transform, ST_Union

from libadalina.graph.constants import DEFAULT_EPSG
from libadalina.graph.coordinate_formats import EPSGFormats
from libadalina.readers.reader import MandatoryColumns, OneWay
from libadalina.sedona_integration.sedona_configuration import get_sedona_context
from pyspark.sql import functions as F

from libadalina.utils.spark_utils import get_spark_dataframe
from libadalina.writers.to_geopackage import dataframe_to_geopackage

def all_columns_except_geometry(df: DataFrame):
    return [F.col(c) for c in df.columns if c != 'geometry']

def get_column_name(col: Column) -> str:
    return col._jc.toString().split('.')[-1]

def explode_multipoint_to_points(df: DataFrame) -> DataFrame:
    return (df
            .select(F.explode(ST_Dump(ST_Points(F.col("geometry")))).alias("geometry"))
            .distinct()).select(F.expr('uuid()').alias('uuid'), F.col('geometry'))

def explode_multiline_to_lines(df: DataFrame) -> DataFrame:
    return (df
            .select(*all_columns_except_geometry(df),
                    F.explode(ST_LineSegments(F.col("geometry"))).alias('geometry'))
            )


def convert_to_default_epsg(df: DataFrame, source_crs: int) -> DataFrame:
    return df.withColumn("geometry", ST_Transform(F.col("geometry"), F.lit(f'EPSG:{source_crs}'), F.lit(f'EPSG:{DEFAULT_EPSG}')))


def join_lines_with_points(lines_df: DataFrame, points_df: DataFrame) -> DataFrame:
    return (lines_df
            .join(points_df, on=ST_Intersects(lines_df.geometry, points_df.geometry), how='inner')
            .groupby(lines_df.geometry)
                .agg(
                    *(F.first(c).alias(get_column_name(c)) for c in all_columns_except_geometry(lines_df)),
                    F.collect_list(points_df.uuid).alias('points_uuid'),
                    F.collect_list(points_df.geometry).alias('points_geometry'),
                )
            )

def aggregate_join(road_map: DataFrame, other_map: DataFrame,
                   road_area: int,
                   *functions: Callable[[DataFrame, Column],Column]) -> DataFrame:
    road_map = (road_map.select('*',
                               ST_Union(
                                   ST_Buffer(road_map.geometry, road_area / 2, F.lit(True), parameters=F.lit('endcap=flat side=left')),
                                   ST_Buffer(road_map.geometry, road_area / 2, F.lit(True), parameters=F.lit('endcap=flat side=right'))
                               ).alias('boxed_geometry'))
                )
    # dataframe_to_geopackage(road_map.drop('geometry').withColumnRenamed('boxed_geometry', 'geometry'), 'road_boxed.gpkg')
    return (road_map
            .join(other_map, on=ST_Intersects(road_map.boxed_geometry, other_map.geometry), how='inner')
            .groupby(road_map.geometry)
                .agg(
                    *(F.first(c).alias(get_column_name(c)) for c in all_columns_except_geometry(road_map)),
                    *(f(other_map, ST_Area(ST_Intersection(road_map.boxed_geometry, other_map.geometry)) / ST_Area(other_map.geometry)) for f in functions)
                )
            ).drop('boxed_geometry')

def add_nodes(graph: nx.Graph, df: DataFrame) -> nx.Graph:
    for row in df.collect():
        node_id = row['uuid']
        graph.add_node(node_id, **row.asDict())
    return graph

def _add_arc(graph: nx.Graph, point1, point2, direction, data: dict):
    if direction == OneWay.Forward.value:
        graph.add_edge(point1, point2, **data)
    elif direction == OneWay.Backward.value:
        graph.add_edge(point2, point1, **data)
    else:
        graph.add_edge(point1, point2, **data)
        graph.add_edge(point2, point1, **data)


def add_arcs(graph: nx.Graph, df: DataFrame) -> nx.Graph:
    for row in df.collect():
        points = row['points_uuid']
        point_geometry = row['points_geometry']
        direction = row[MandatoryColumns.oneway.value]
        if len(points) != 2:
            raise Exception(f"invalid number of points in line: {points}")
        point1, point2 = points if point_geometry[0].coords[0] == row['geometry'].coords[0] else points[::-1]
        _add_arc(graph, point1, point2, direction, row.asDict())

    return graph

def reduce_graph(graph: nx.Graph) -> nx.Graph:
    reduced = graph.copy()
    #TODO: da completare

    count = 0
    while True:
        nodes_to_reduce = [n for n in reduced.nodes() if reduced.degree(n) == 2]
        if not nodes_to_reduce:
            break

        for node in nodes_to_reduce:
            neighbors = list(reduced.neighbors(node))
            edges = reduced.edges(node, data=True)
            print(node,  reduced.degree(node), edges, neighbors, nodes_to_reduce)
            if len(neighbors) != 2:
                continue

            n1, n2 = neighbors
            edge1_data = reduced.edges[node, n1, 0]
            edge2_data = reduced.edges[node, n2, 0]

            merged_line = shapely.line_merge(shapely.MultiLineString([edge1_data['geometry'], edge2_data['geometry']]))
            coords = list(merged_line.coords)
            merged_data = {
                'geometry': shapely.LineString([shapely.geometry.Point(coords[0]), shapely.geometry.Point(coords[-1])]),
            }

            reduced.remove_node(node)
            reduced.add_edge(n1, n2, **merged_data)


    return reduced

@dataclasses.dataclass
class _GraphJoinParams:
    dataframe: pd.DataFrame | gpd.GeoDataFrame | DataFrame | str
    epsg: EPSGFormats
    road_area: int
    functions: tuple[Callable[[DataFrame, Column], Column], ...] = dataclasses.field(default_factory=tuple)

class GraphFactory:

    def __init__(self, roads_df: pd.DataFrame | gpd.GeoDataFrame | DataFrame | str, epsg: EPSGFormats | None = None):
        self._name: str = 'graph'
        self._roads_df: pd.DataFrame | gpd.GeoDataFrame | DataFrame | str = roads_df
        if epsg is None and not isinstance(roads_df, gpd.GeoDataFrame):
            raise ValueError("epsg must be specified if roads_df is not a GeoDataFrame")
        self._epsg: EPSGFormats = epsg if not isinstance(roads_df, gpd.GeoDataFrame) else EPSGFormats.from_code(roads_df.crs.to_epsg())
        self._table_joins: list[_GraphJoinParams] = []
        self._reduce: bool = False # TODO: da implementare
        self._sedona_master: str | None = None

    def name(self, name: str):
        self._name = name
        return self

    def join_with(self, df: pd.DataFrame | gpd.GeoDataFrame | DataFrame, epsg: EPSGFormats, road_area: int,
                 *functions: Callable[[DataFrame, Column], Column]):
        self._table_joins.append(_GraphJoinParams(df, epsg, road_area, functions))
        return self

    def reduce(self):
        self._reduce = True
        return self

    def with_sedona_master(self, host: str, port: int):
        self._sedona_master = f"spark://{host}:{port}"
        return self

    def build(self) -> nx.Graph:
        sedona = get_sedona_context()

        df = get_spark_dataframe(sedona, self._roads_df)
        df = convert_to_default_epsg(df, self._epsg.value)

        sedona.conf.set("spark.sql.debug.maxToStringFields", '100')
        # df.show(truncate=False)

        lines_df = explode_multiline_to_lines(df)
        if self._table_joins:
            for join in self._table_joins:
                join_df = convert_to_default_epsg(get_spark_dataframe(sedona, join.dataframe), join.epsg.value)
                lines_df = aggregate_join(lines_df, join_df, join.road_area, *join.functions)
        # dataframe_to_geopackage(lines_df, 'road_map.gpkg')
        # lines_df.show(truncate=False)
        points_df = explode_multipoint_to_points(df)

        lines_df = join_lines_with_points(lines_df, points_df)
        # lines_df.show(truncate=False)

        graph = add_arcs(add_nodes(nx.DiGraph(), points_df), lines_df)
        # graph = reduce_graph(graph)

        graph.name = self._name

        return graph