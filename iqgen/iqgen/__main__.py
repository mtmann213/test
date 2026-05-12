"""CLI entry point for IQ Signal Generator."""

import argparse
import logging
import sys
from pathlib import Path

from iqgen import IQGenerator
from iqgen.config import create_config

PROJECT_ROOT = Path(__file__).parent.parent
EXAMPLE_CONFIG = PROJECT_ROOT / "config" / "iq_generator.yaml"


def main():
    parser = argparse.ArgumentParser(
        description="Generate IQ files in cf32 or SigMF format from YAML config"
    )
    parser.add_argument(
        "config",
        nargs="?",
        default=str(EXAMPLE_CONFIG),
        help="Path to YAML config file (default: config/iq_generator.yaml)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (use -vv for debug)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Override output directory from config",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.WARNING
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format="%(levelname)s %(name)s: %(message)s")

    # Load config
    config_path = Path(args.config)
    if not config_path.is_file():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = create_config(str(config_path))

    # Override output dir if specified
    if args.output_dir:
        config.output_dir = args.output_dir

    print(f"Generating: {config.name} ({config.modulation})")
    print(f"  Bitrate: {config.bitrate/1000:.1f} kbps")
    print(f"  Sample rate: {config.sample_rate/1e6:.1f} Msps")
    print(f"  Samples/symbol: {config.samples_per_symbol}")
    print(f"  Filter: {config.filter_type}")
    print(f"  Format: {config.output_format}")
    print(f"  Output dir: {config.output_dir}")
    print()

    gen = IQGenerator(config)
    paths = gen.generate_and_write()
    print(f"Output files:")
    for p in paths:
        if p:
            print(f"  {p}")


if __name__ == "__main__":
    main()
