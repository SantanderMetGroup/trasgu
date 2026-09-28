#!/usr/bin/env python3
"""Refit the reference models to existing observations without regenerating data."""

import argparse
from pathlib import Path

import numpy as np
import pyvinecopulib as pv
import yaml
from trasgu import Trasgu


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    data = np.loadtxt(run / "vinecop_samples.txt", ndmin=2)
    matrix = Trasgu(str(run / "trasgu.yaml")).get_matrix(252000)[0]
    bicop = pv.Bicop(pv.clayton, parameters=np.array([[3.1819]]))
    model = pv.Vinecop.from_structure(
        matrix=matrix, pair_copulas=[[bicop] * n for n in range(6, 0, -1)]
    )
    controls = dict(
        tree_criterion="tau",
        selection_criterion="aic",
        parametric_method="mle",
        show_trace=False,
    )
    dissmann = pv.Vinecop.from_data(
        data, controls=pv.FitControlsVinecop(family_set=pv.one_par, **controls)
    )
    fixed = pv.Vinecop.from_data(
        data,
        matrix=matrix,
        controls=pv.FitControlsVinecop(family_set=[pv.clayton], **controls),
    )
    results = dict(
        aic_dissmann=float(dissmann.aic()),
        aic_fixed_matrix_clayton=float(fixed.aic()),
        aic_ground_truth=float(model.aic(data)),
        matrix=dissmann.matrix.tolist(),
    )
    (run / "references.yaml").write_text(yaml.safe_dump(results, sort_keys=False))


if __name__ == "__main__":
    main()
