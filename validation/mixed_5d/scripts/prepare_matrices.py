"""Prepare both five-variable catalogues for the mixed-family validation."""

import argparse
from pathlib import Path

from validation._shared.chimera import DEFAULT_ZARR, prepare_catalogues
from validation.mixed_5d.scripts.model import MATRIX


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--chimera-url", default=DEFAULT_ZARR)
    args = parser.parse_args()
    prepare_catalogues(args.output, args.chimera_url, MATRIX)


if __name__ == "__main__":
    main()
