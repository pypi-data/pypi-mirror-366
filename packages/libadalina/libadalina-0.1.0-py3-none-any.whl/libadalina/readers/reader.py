from enum import Enum

import geopandas as gpd

from libadalina.exceptions.input_file_exception import InputFileException

class MandatoryColumns(Enum):
    id = 'id'
    name = 'name'
    oneway = 'oneway'

class OneWay(Enum):
    Forward = 'forward'
    Backward = 'backward'
    Both = 'both'

class MapReader:

    def map_and_reduce(self, gdf: gpd.GeoDataFrame, column_map: dict[MandatoryColumns, str]) -> gpd.GeoDataFrame:

        for key, value in column_map.items():
            gdf[key.value] = gdf[value]

        gdf = gdf[['geometry'] + [c.value for c in MandatoryColumns]]

        for c in MandatoryColumns:
            if c.value not in gdf.columns:
                raise InputFileException(f"missing column {c.value} in dataframe")
        return gdf


