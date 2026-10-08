"""Download Madrid's official address register to data/direcciones.csv."""
from pathlib import Path
from urllib.request import Request, urlopen
import shutil
import sys

DATA_URL = (
    "https://datos.madrid.es/en/en/dataset/213605-0-callejero-oficial-madrid/"
    "resource/213605-4-callejero-oficial-madrid-csv/download/"
    "213605-4-callejero-oficial-madrid-csv.csv"
)
OUTPUT = Path(__file__).resolve().parent / "data" / "direcciones.csv"


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    request = Request(DATA_URL, headers={"User-Agent": "madrid-route-planner/1.0"})
    temporary = OUTPUT.with_suffix(".csv.part")
    try:
        print("Downloading the official Madrid address dataset (about 33 MB)...")
        with urlopen(request, timeout=90) as response, temporary.open("wb") as target:
            shutil.copyfileobj(response, target)
        temporary.replace(OUTPUT)
        print(f"Saved dataset to: {OUTPUT}")
        return 0
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        print(f"Download failed: {exc}", file=sys.stderr)
        print(f"You can download it manually from: {DATA_URL}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
