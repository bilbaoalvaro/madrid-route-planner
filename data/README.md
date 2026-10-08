# Local data files

The large data files below are intentionally not committed to Git.

- `direcciones.csv`: download with `python download_addresses.py`. It comes from the [Ayuntamiento de Madrid open-data portal](https://datos.madrid.es/dataset/213605-0-callejero-oficial-madrid/downloads).
- `madrid.graphml`: generated automatically by OSMnx on the first run of `python gps.py`, when an internet connection is available. The underlying road data comes from [OpenStreetMap](https://www.openstreetmap.org/copyright) and is available under the ODbL.
