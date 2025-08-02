import os.path
from shapely.io import from_wkt

from libadalina.exceptions.input_file_exception import InputFileException
from libadalina.readers.reader import MapReader, MandatoryColumns, OneWay
import geopandas as gpd
import pandas as pd

class OpenStreetMapReader(MapReader):
    CRS = 4326

    def read(self, file_path: str) -> gpd.GeoDataFrame:
        if file_path.endswith('.csv'):
            return self.read_csv(file_path)
        elif file_path.endswith('.shp'):
            return self.read_shp(file_path)

        raise InputFileException(f'no reader found for file {file_path}')

    def read_csv(self, file_path: str) -> gpd.GeoDataFrame:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'file {file_path} does not exist')

        df = pd.read_csv(file_path, sep=',')
        return self.from_dataframe(df)

    def read_shp(self, file_path: str) -> gpd.GeoDataFrame:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'file {file_path} does not exist')

        return self._map_columns(gpd.read_file(file_path))

    def from_dataframe(self, df: pd.DataFrame) -> gpd.GeoDataFrame:
        df.loc[:, 'geometry'] = df['geometry'].apply(from_wkt)
        return self._map_columns(gpd.GeoDataFrame(df, geometry='geometry', crs=self.CRS))

    def _map_columns(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        gdf['name'] = gdf['name'].fillna('')
        gdf = self.map_and_reduce(gdf, {
            MandatoryColumns.id: 'osm_id',
            MandatoryColumns.name: 'name',
            MandatoryColumns.oneway: 'oneway'
        })
        
        oneway_mapping = {
            'F': OneWay.Forward.value,
            'T': OneWay.Backward.value,
            'B': OneWay.Both.value
        }
        gdf.loc[:, MandatoryColumns.oneway.value] = gdf[MandatoryColumns.oneway.value].map(oneway_mapping).fillna(
            OneWay.Both.value)
        return gdf