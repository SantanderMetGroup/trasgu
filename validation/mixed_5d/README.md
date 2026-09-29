# Mixed-family five-variable validation

## Design

5 variables, 6 Clayton edges with parameter 3.1819 and 4 Gaussian edges
with correlation parameter 0.5; all rotations are zero.
100 simulations, 300 observations each, master seed 20260929.
The generating matrix (Chimera ID 61) is defined in
[`scripts/model.py`](scripts/model.py).

**Both methods fit all 480 matrices to every dataset: 48,000 fits each.**
Trasgu reads Chimera in Zarr; a manual Python loop reads the original TU Delft
files. Both use identical observations and fitting controls. Generation uses
families from `pyvinecopulib.one_par`; exhaustive fitting and Dißmann selection
use `one_par`, AIC family selection and maximum likelihood estimation.
The fixed reference retains the generating structure and families and refits
parameters.

## Run

From the repository root, after `uv sync --frozen --extra benchmarks`:

```bash
uv run --no-sync python validation/mixed_5d/run_validation.py --run-dir validation/mixed_5d/runs/reproduce-full --iterations 100 --observations 300 --seed 20260929 --cores 4
```

Preparation downloads and verifies both catalogues. Add `--dry-run` to inspect
jobs; use `--iterations 1` in a separate directory for a pilot. Repeat the
command to resume; choose a new directory when changing settings or code.
Generated inputs, full fits and logs remain in `runs/`, outside Git.

## Results

**All 48,000 paired AICs agree** within `1e-5`; the maximum absolute difference
is **4.99996303915e-7**, consistent with Trasgu's six-decimal output.
Both methods reproduce the same exhaustive result within numerical tolerance.

- [Comparison table](results/aic_comparison.csv) and [summary](results/summary.json).
- [Figure](results/aic_differences.png): absolute AIC differences of exhaustive
  and Dißmann fits from the refitted generating model.
- [Reproducibility record](results/reproducibility.json): settings, versions,
  source hashes and input checksums.

The CSV column `aic_fixed_matrix_clayton` refers here to the refitted mixed
Clayton/Gaussian generating model.
