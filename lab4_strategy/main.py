from __future__ import annotations

import argparse

from src.config_loader import ConfigLoader
from src.dataset_service import DatasetService
from src.strategy_factory import OutputStrategyFactory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Laboratory work #4: GoF Strategy pattern for output to console/file/redis/kafka"
    )
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download dataset from the remote source before reading it",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ConfigLoader.load(args.config)

    dataset_config = config["dataset"]
    output_config = config["output"]

    dataset_service = DatasetService(
        url=dataset_config["url"],
        local_csv_path=dataset_config["local_csv_path"],
        timeout_seconds=int(dataset_config.get("timeout_seconds", 60)),
        request_headers=dataset_config.get("request_headers", {}),
    )

    if args.download:
        saved_path = dataset_service.download_to_file()
        print(f"Dataset downloaded to: {saved_path}")

    rows = dataset_service.read_rows(limit=output_config.get("line_limit"))
    lines = dataset_service.format_rows(rows)

    strategy = OutputStrategyFactory.create(output_config)
    strategy.write(lines)

    print(f"Written {len(lines)} line(s) using strategy: {output_config['strategy']}")


if __name__ == "__main__":
    main()
