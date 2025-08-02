from pyspark import StorageLevel
from pyspark.sql import SparkSession
import pandas as pd
import geopandas as gpd
from pyspark.sql import DataFrame

def get_spark_dataframe(sedona: SparkSession, df: pd.DataFrame | gpd.GeoDataFrame | DataFrame | str) -> DataFrame:
    if isinstance(df, DataFrame):
        return df
    if isinstance(df, gpd.GeoDataFrame):
        return sedona.createDataFrame(df)
    if isinstance(df, pd.DataFrame):
        return sedona.createDataFrame(df)
    if isinstance(df, str):
        return sedona.table(df)
    raise TypeError(f"Unsupported type {type(df)}. Expected pd.DataFrame, gpd.GeoDataFrame, DataFrame or str.")

def set_spark_dataset(sedona: SparkSession, df: pd.DataFrame | gpd.GeoDataFrame | DataFrame, name: str):
    if not isinstance(df, DataFrame):
        df = sedona.createDataFrame(df)
    df.createOrReplaceTempView(name)
    return df