import argparse

from game.app import App


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all-features",
        action="store_true",
        help="Ignore stage-based progression and enable all gameplay features from stage 1.",
    )
    args = parser.parse_args()
    App(all_features=args.all_features)
