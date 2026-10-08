# Madrid Route Planner

A Python GPS prototype that calculates routes between street addresses in Madrid. The project represents the road network as a directed weighted graph, implements Dijkstra's shortest-path algorithm, and displays the resulting route on an interactive map.

**Academic team project** for Discrete Mathematics, BSc in Mathematical Engineering and Artificial Intelligence, ICAI (2025–2026). Developed in collaboration by **Álvaro Bilbao Pardo and Javier Arraiza Arribas**.

## What it does

- Looks up street addresses using Madrid's official address register and their coordinates.
- Builds a drivable street network for Madrid from OpenStreetMap using OSMnx.
- Implements Dijkstra's algorithm and path reconstruction in `grafo_pesado.py`.
- Offers three routing criteria:
  - **Shortest distance:** minimises road length.
  - **Estimated travel time:** uses available `maxspeed` values and fallback speeds based on road type.
  - **Penalised travel time:** adds a fixed 24-second cost per graph edge. This is an illustrative heuristic, not live traffic data or a verified count of traffic lights.
- Creates an HTML route map with Folium and opens it in the default browser.

Estimated travel times are approximations; the project does not use live traffic, closures, or real-time routing information.

## Requirements

- Python 3.10 or newer
- An internet connection on the first run, to download the street graph from OpenStreetMap

## Setup

1. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   # macOS / Linux
   source .venv/bin/activate
   # Windows PowerShell: .venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Download the official address register. The CSV is kept out of the Git repository because it is a large, frequently updated public dataset.

   ```bash
   python download_addresses.py
   ```

4. Start the route planner.

   ```bash
   python gps.py
   ```

5. Enter addresses in the format `Calle de Alberto Aguilera, 1`, then select the routing criterion. The first run may take a while while OSMnx downloads and saves the road graph in `data/madrid.graphml`.

The generated route map is written to `results/route.html`. The downloaded address file, cached road graph, and generated map are excluded by `.gitignore`.

## Tests

Run the graph-algorithm tests with Python's standard library:

```bash
python -m unittest discover -s tests -v
```

The tests use small synthetic graphs and do not require either of the large geographic datasets.

## Data sources and attribution

- **Madrid address register:** Ayuntamiento de Madrid, *Callejero oficial de Madrid — Relación de direcciones vigentes, con coordenadas*. The official open-data portal lists the resource under **CC BY 4.0**. The download script retrieves the CSV from the portal: [dataset page](https://datos.madrid.es/dataset/213605-0-callejero-oficial-madrid/downloads).
- **Road network:** © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright). OpenStreetMap data is available under the [Open Database License (ODbL)](https://www.openstreetmap.org/copyright). The graph is generated locally through OSMnx and is not bundled in this repository.

## Project structure

```text
madrid-route-planner/
├── gps.py                 # Command-line interface, route costs and map output
├── callejero.py           # Address lookup and road-graph loading
├── grafo_pesado.py        # Dijkstra, path reconstruction, Prim and Kruskal
├── download_addresses.py  # Downloads Madrid's official address dataset
├── requirements.txt
├── tests/
│   └── test_grafo.py
└── data/
    └── README.md          # Data files are downloaded/generated locally
```

## Scope and limitations

This is an academic prototype rather than a production navigation system. Address matching is exact, travel speeds are estimates, and the fixed per-edge penalty is a simple experiment rather than traffic-light detection. The road graph is fetched from OpenStreetMap when it is not present locally.
