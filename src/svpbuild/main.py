"""
The main entry point for the svpbuild CLI.

Parses command-line arguments, orchestrates the discovery and compilation
of assets, and writes the final JSON files and copied assets to the output directory.
"""

import argparse
import logging
import sys
import time
from importlib.metadata import PackageNotFoundError, metadata, version
from pathlib import Path

try:
    __version__ = version("svpbuild")
    __description__ = metadata("svpbuild").get("Summary", "Build Content Patcher portrait mods.")
except PackageNotFoundError:
    __version__ = "unknown"
    __description__ = "Build Content Patcher portrait mods."

from svpbuild.builder import Builder
from svpbuild.loader import Loader


def parse_args() -> argparse.Namespace:
    """Parses and returns command-line arguments."""
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        "source",
        nargs="?",
        help="Path to the mod source directory containing assets/ and manifest.json",
        type=str,
        default=".",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output directory",
        type=str,
        default="build",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose (DEBUG) logging",
        action="store_true",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args()


def setup_logging(verbose: bool) -> logging.Logger:
    """Configures the logging format and level."""
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger


def main():
    """Main execution loop for the svpbuild CLI."""
    args = parse_args()
    logger = setup_logging(args.verbose)

    source_dir = Path(args.source).resolve()
    output_dir = Path(args.output).resolve()

    logger.debug(f"Source directory resolved to: {source_dir}")

    if not source_dir.exists() or not source_dir.is_dir():
        logger.error(f"Source directory does not exist or is not a directory: {source_dir}")
        sys.exit(1)

    try:
        loader = Loader(source_dir)
    except Exception as e:
        if args.verbose:
            logger.exception("Failed to load assets")
        else:
            logger.error(f"Failed to load assets: {e}")
        sys.exit(1)

    logger.info("Building content pack...")

    builder = Builder(loader, output_dir)
    mod_out_dir = builder.build()

    logger.info(f"Successfully built mod in {mod_out_dir}")


if __name__ == "__main__":
    main()
