"""Shared scientific definition of the five-variable ESREL validation."""

import numpy as np
import pyvinecopulib as pv

N_VARIABLES = 5
N_MATRICES = 480
CLAYTON_PARAMETER = 3.1819
# pyvinecopulib's anti-diagonal convention, obtained by reversing columns.
MATRIX = np.array(
    [
        [5, 5, 4, 2, 4],
        [0, 4, 5, 4, 2],
        [0, 0, 2, 5, 1],
        [0, 0, 0, 1, 5],
        [0, 0, 0, 0, 3],
    ]
)[:, ::-1].copy()


def generating_model():
    pairs = [
        [
            pv.Bicop(pv.clayton, parameters=np.array([[CLAYTON_PARAMETER]]))
            for _ in range(N_VARIABLES - tree - 1)
        ]
        for tree in range(N_VARIABLES - 1)
    ]
    return pv.Vinecop.from_structure(matrix=MATRIX, pair_copulas=pairs)


def simulate(observations, seed, iteration):
    """Independent, deterministic stream per iteration, independent of job order."""
    seeds = (
        np.random.SeedSequence([seed, iteration]).generate_state(4) & 0x7FFFFFFF
    ).tolist()
    return generating_model().simulate(observations, seeds=seeds), seeds
