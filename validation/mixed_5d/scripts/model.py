"""Five-variable generating vine with six Clayton and four Gaussian edges."""

import numpy as np
import pyvinecopulib as pv

MATRIX = np.array(
    [
        [4, 2, 4, 5, 5],
        [2, 4, 5, 4, 0],
        [1, 5, 2, 0, 0],
        [5, 1, 0, 0, 0],
        [3, 0, 0, 0, 0],
    ]
)
FAMILIES = [
    ["clayton", "gaussian", "gaussian", "clayton"],
    ["clayton", "gaussian", "clayton"],
    ["clayton", "gaussian"],
    ["clayton"],
]
PARAMETERS = {"clayton": 3.1819, "gaussian": 0.5}
MODEL_DESCRIPTION = {
    "variables": 5,
    "matrix": MATRIX.tolist(),
    "families_by_tree": FAMILIES,
    "parameters": PARAMETERS,
    "rotation": 0,
}


def generating_model():
    pairs = [
        [
            pv.Bicop(
                family=getattr(pv.BicopFamily, name),
                rotation=0,
                parameters=np.array([[PARAMETERS[name]]]),
            )
            for name in tree
        ]
        for tree in FAMILIES
    ]
    return pv.Vinecop.from_structure(matrix=MATRIX, pair_copulas=pairs)


def simulate(observations, seed, iteration):
    seeds = (
        np.random.SeedSequence([seed, iteration]).generate_state(4) & 0x7FFFFFFF
    ).tolist()
    return generating_model().simulate(observations, seeds=seeds), seeds
