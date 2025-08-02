from pyspark.sql import SparkSession
from sedona.spark import SedonaContext
import pandas as pd

pd.DataFrame.iteritems = pd.DataFrame.items

def _get_sedona_master_configuration(master_host: str) -> SparkSession:
    spark = (SparkSession.builder
            .appName("Adalina")
            .master(master_host)
            .config(
                "spark.jars.packages",
                "org.apache.sedona:sedona-spark-3.3_2.12:1.7.1,"
                "org.datasyslab:geotools-wrapper:1.7.1-28.5",
            )
            .config(
                "spark.jars.repositories",
                "https://artifacts.unidata.ucar.edu/repository/unidata-all"
            )
            .config("spark.executor.instances", 1)
            .config("spark.executor.cores", "1")
            .config("spark.executor.memory", "2G")
            .getOrCreate())
    return SedonaContext.create(spark)

def _sedona_configuration() -> SparkSession:
    config = (
        SedonaContext.builder()
             .appName("Adalina")
             .config(
                "spark.jars.packages",
                "org.apache.sedona:sedona-spark-3.3_2.12:1.7.1,"
                "org.datasyslab:geotools-wrapper:1.7.1-28.5",
            )
            .config("spark.driver.memory", "20g")
            .config(
                "spark.jars.repositories",
                "https://artifacts.unidata.ucar.edu/repository/unidata-all"
            )
            .getOrCreate()
    )
    return SedonaContext.create(config)

_sedona_context: SparkSession | None = None

def get_sedona_context(master: str | None = None) -> SparkSession:
    global _sedona_context
    if _sedona_context is None:
        if master is None:
            _sedona_context = _sedona_configuration()
        else:
            _sedona_context = _get_sedona_master_configuration(master)
    return _sedona_context