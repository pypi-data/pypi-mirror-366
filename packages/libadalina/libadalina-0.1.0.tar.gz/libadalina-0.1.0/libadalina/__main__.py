import click
from pandas.core.interchange.dataframe_protocol import DataFrame

from libadalina.graph.coordinate_formats import EPSGFormats
from libadalina.readers.open_street_map import OpenStreetMapReader
from libadalina.graph.graph_factory import GraphFactory
from libadalina.sedona_integration.sedona_configuration import get_sedona_context
from libadalina.utils.networkx_utils import get_node_of_address
from libadalina.utils.spark_utils import set_spark_dataset, get_spark_dataframe
from libadalina.utils.timing import Timing
from libadalina.writers.to_geopackage import graph_to_geopackage, path_to_geopackage
import networkx as nx
import geopandas as gpd
from pyspark.sql import functions as F
import logging
import os
import jdk

_ROAD_MAP = 'road_map'
_POPULATION = 'population'

_REMOTE_HOST = 'localhost'
_REMOTE_PORT = 7077


def install_jdk_if_needed():
    if 'JAVA_HOME' not in os.environ:
        version = '17'
        jre_path = os.path.join(jdk._JRE_DIR, version)

        if os.path.exists(jre_path):
            logging.info(f'JAVA_HOME not set but JRE already downloaded')
            os.environ['JAVA_HOME'] = jre_path
        else:
            logging.info('JAVA_HOME not set, installing JRE...')
            java_home = jdk.install(version, jre=True)
            os.environ['JAVA_HOME'] = java_home
            os.symlink(java_home, jre_path)

    logging.info(f'JAVA_HOME set to {os.environ.get("JAVA_HOME")}')


def get_context(remote = False):
    return get_sedona_context() if not remote else get_sedona_context(f'spark://{_REMOTE_HOST}:{_REMOTE_PORT}')


def load_dataset_from_disk(remote: bool, create_spark_view = False) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    reader = OpenStreetMapReader()
    gfd = reader.read('./tests/readers/samples/milano/gis_osm_roads_free_1.csv')
    # gdf = gdf[(
        #     (gdf['name'].str.contains('celoria', case=False)) |
        #     (gdf['name'].str.contains('ponzio', case=False)) |
        #     (gdf['name'].str.contains('colombo', case=False)) |
        #     (gdf['name'].str.contains('golgi', case=False)) |
        #     (gdf['name'].str.contains('venezian', case=False)) |
        #     (gdf['name'].str.contains('gorini', case=False))
        # )]
    population = gpd.read_file('./tests/readers/samples/population-north-italy/nord-italia.gpkg',
                               layer='census2021')
    population = population.to_crs('EPSG:4326')

    if create_spark_view:
        set_spark_dataset(get_context(remote), gfd, _ROAD_MAP)
        set_spark_dataset(get_context(remote), population, _POPULATION)

    return gfd, population

def load_dataset_from_spark(use_remote=False) -> tuple[DataFrame, DataFrame]:
    gfd = get_spark_dataframe(get_context(use_remote), _ROAD_MAP)
    population = get_spark_dataframe(get_context(use_remote), _POPULATION)
    return gfd, population

@click.command()
@click.option('--use-remote', is_flag=True, help=f'Use a remote Spark cluster on {_REMOTE_HOST}:{_REMOTE_PORT}')
@click.option('--load-spark-datasets', is_flag=True, help='Load datasets to Spark and retrieves them as DataFrame for processing instead of loading directly from disk')
@click.pass_context
def run(ctx, use_remote, load_spark_datasets):
    logging.basicConfig(level=logging.INFO)

    with Timing('Time installing JDK: {}'):
        install_jdk_if_needed()

    with Timing('Time loading datasets: {}'):
        if load_spark_datasets:
            load_dataset_from_disk(use_remote, True)

        gfd, population = load_dataset_from_spark(use_remote) if load_spark_datasets else load_dataset_from_disk(use_remote, False)

    with Timing('Time building graph: {}'):
        graph_factory = GraphFactory(gfd, EPSGFormats.from_code(OpenStreetMapReader.CRS))

        factory = graph_factory.name('Milano')
        if use_remote:
            factory = factory.with_sedona_master(_REMOTE_HOST, _REMOTE_PORT)
        graph = factory.join_with(population, EPSGFormats.EPSG4326, 100, lambda df, area: F.sum(df.T * area).alias('population')).build()
        graph_to_geopackage(graph, 'milan_graph.gpkg')
        print(f'Number of nodes: {len(graph.nodes)}, Number of edges: {len(graph.edges)}')

    with Timing('Time computing shortest path: {}'):
        graph_to_geopackage(graph, 'milano_exported.gpkg')
        source = get_node_of_address(graph, 'luini')
        destination = get_node_of_address(graph, 'gorini')
        # print(source, destination)

        shortest_path = nx.shortest_path(graph, source, destination, weight='population')
        path_to_geopackage(graph, shortest_path, 'shortest_path_population.gpkg')
        cost = nx.path_weight(graph, shortest_path, 'population')
        print(f'Shortest path from {source} to {destination} with population weight: {cost}')
        shortest_path = nx.shortest_path(graph, source, destination)
        path_to_geopackage(graph, shortest_path, 'shortest_path.gpkg')
        cost = len(shortest_path) - 1
        print(f'Shortest path from {source} to {destination} with default weight: {cost}')


if __name__ == "__main__":
    run()