from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.constants import METRICS_PATH
from game.metrics import MetricsStore


def main():
    store = MetricsStore(METRICS_PATH)
    summary = store.summary()
    print(f"runs: {summary['runs']}")
    print(f"mode_count: {summary['mode_count']}")
    print(f"protocol_count: {summary['protocol_count']}")


if __name__ == "__main__":
    main()
