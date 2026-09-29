"""Download the five-variable catalogues and verify their matrix correspondence."""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.request import urlopen

import fsspec
import numpy as np
import pyvinecopulib as pv
import zarr

from model import MATRIX, N_MATRICES

sys.path.insert(0, str(Path(__file__).parent / "manual"))
from get_matrices import get_matrices

FILES = {
    "submats_5_T6.pbz2": "990bd2a4-e3fd-41c9-81a0-6d91d0944328",
    "submats_5_T7.pbz2": "5720584d-2af6-4751-970f-1e6a72cd32ec",
    "submats_5_T8.pbz2": "947be791-f54d-4cf0-99e0-3f7f9ee334bd",
}
EXPECTED_SHA256 = {
    "submats_5_T6.pbz2": "482b0f41c8395ef1af65eed0ac18899449ce0dda129e66eaf278e9b1fb6aa8ae",
    "submats_5_T7.pbz2": "7266eb6a6653c760a2e4423f921ae874e4a1bcfab5e34454b1388bd85e066f1e",
    "submats_5_T8.pbz2": "21e265740ce43f619a75eff820110d9df3d19b77d3f086a158d947c24b996625",
}
EXPECTED_MATRICES_SHA256 = (
    "b115647e21385306c9bba2ca67af1f67d9e416b9b74d838b9f212d1b4b15f7bd"
)
BASE = "https://data.4tu.nl/file/905e1d81-6fc0-472a-91b3-000ec57454ff/"
DEFAULT_ZARR = "http://meteo.unican.es/work/chimera.zarr"


def matrix_mapping(canonical, manual):
    if canonical.shape != (N_MATRICES, 5, 5) or manual.shape != canonical.shape:
        raise ValueError(
            "Both catalogues must contain exactly 480 matrices of shape 5 x 5"
        )
    lookup = {tuple(m.ravel()): i for i, m in enumerate(manual)}
    if len(lookup) != N_MATRICES:
        raise ValueError("Duplicate legacy matrices")
    mapping = [lookup[tuple(m.ravel())] for m in canonical]
    if len(set(mapping)) != N_MATRICES:
        raise ValueError("Catalogues are not in one-to-one correspondence")
    for matrix in canonical:
        pv.RVineStructure.from_matrix(matrix)  # Validate orientation and structure.
    return mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--chimera-url", default=DEFAULT_ZARR)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    legacy = args.output / "legacy"
    legacy.mkdir(exist_ok=True)
    sources = {}
    for name, file_id in FILES.items():
        url = BASE + file_id
        # Always refresh on an explicit rerun of this preparation rule.
        with urlopen(url, timeout=120) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != EXPECTED_SHA256[name]:
            raise ValueError(
                f"Checksum mismatch for {name}; refusing to load a changed catalogue"
            )
        (legacy / name).write_bytes(content)
        sources[name] = {"url": url, "sha256": hashlib.sha256(content).hexdigest()}
    # The legacy files are pickles from the original, explicitly listed 4TU record.
    manual = np.asarray([m.matrix for m in get_matrices(str(legacy) + "/", nodes=5)])
    source = args.chimera_url
    store = fsspec.get_mapper(source) if "://" in source else source
    canonical = np.asarray(zarr.open_group(store, mode="r")["matrices5"][:])
    if (
        hashlib.sha256(canonical.astype("uint8").tobytes()).hexdigest()
        != EXPECTED_MATRICES_SHA256
    ):
        raise ValueError(
            "The five-variable Zarr catalogue differs from the verified catalogue"
        )
    mapping = matrix_mapping(canonical, manual)
    target = zarr.open_group(str(args.output / "chimera.zarr"), mode="w")
    target.create_array("matrices5", data=canonical, chunks=(480, 5, 5))
    generating_ids = [i for i, m in enumerate(canonical) if np.array_equal(m, MATRIX)]
    if len(generating_ids) != 1:
        raise ValueError("Generating matrix is missing or duplicated")
    report = {
        "chimera_url": source,
        "shape": list(canonical.shape),
        "matrices_sha256": hashlib.sha256(
            canonical.astype("uint8").tobytes()
        ).hexdigest(),
        "legacy_sources": sources,
        "canonical_to_manual": mapping,
        "generating_matrix_id": generating_ids[0],
    }
    (args.output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Verified 480 matrices; generating matrix ID: {generating_ids[0]}")


if __name__ == "__main__":
    main()
