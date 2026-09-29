"""Matrix-level checks shared by scientific validation workflows."""

import csv
from pathlib import Path
import numpy as np

N_MATRICES = 480

# Trasgu stores AIC with six decimal places. Allow rounding and small numeric noise.
AIC_TOLERANCE = 1e-5


def load_fits(path, id_column, aic_column):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    ids = [int(row[id_column]) for row in rows]
    if len(ids) != N_MATRICES or set(ids) != set(range(N_MATRICES)):
        raise ValueError(f"{path}: expected each matrix ID 0..479 exactly once")
    values = np.empty(N_MATRICES)
    for matrix_id, row in zip(ids, rows):
        values[matrix_id] = float(row[aic_column])
    if not np.isfinite(values).all():
        raise ValueError(f"{path}: non-finite AIC")
    return values


def compare_fits(canonical, manual, mapping):
    aligned = manual[np.asarray(mapping)]
    delta = np.abs(canonical - aligned)
    if np.max(delta) > AIC_TOLERANCE:
        i = int(np.argmax(delta))
        raise ValueError(
            f"AIC mismatch for Chimera matrix {i}: {delta[i]:.9g} "
            f"exceeds tolerance {AIC_TOLERANCE}"
        )
    return float(np.max(delta))
