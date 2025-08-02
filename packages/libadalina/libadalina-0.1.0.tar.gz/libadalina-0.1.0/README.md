# libadalina

A library for graph processing with geographic data.

## Installation

### From sources

To install from the source code, clone the repository and run the following commands:

```bash
git clone --recurse-submodules git@gitlab.com:amelia_unimi/libadalina.git
pip install -e libadalina
```

To run the examples on provided samples data, you can clone the submodules as well:

```bash
git clone --recurse-submodules git@gitlab.com:amelia_unimi/libadalina.git
python libadalina/__main__.py 
```

If `JAVA_HOME` environment variable is not set a suitable JDK will be downloaded in `$HOME/.jre` and used automatically.
Not all JRE are supported, so if you encounter issues, you can try the automatically installed version.

## Usage

You can import it in your Python code:

```python
from libadalina.readers.open_street_map import OpenStreetMapReader
from libadalina.graph.graph_factory import GraphFactory
from libadalina.writers.to_geopackage import graph_to_geopackage

# Read data
reader = OpenStreetMapReader()
gfd = reader.read('path/to/your/data.csv')

# Create graph
graph_factory = GraphFactory(gfd)
graph = graph_factory.name('YourGraphName').build()

# Export graph
graph_to_geopackage(graph, 'output.gpkg')
```

## Features

- Read geographic data from OpenStreetMap
- Build and process graph structures
- Export graphs to various formats (GeoPackage, CSV, Shapefile)
- Perform graph operations like shortest path finding

## Requirements

- Python 3.10
- Dependencies:
  - apache-sedona[spark]
  - pyspark
  - pandas
  - geopandas
  - networkx