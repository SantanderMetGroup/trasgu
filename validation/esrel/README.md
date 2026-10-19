# ESREL validation

## Design

5 variables, 10 Clayton edges with parameter 3.1819.
100 simulations, 300 observations each, master seed 20260928.
The generating matrix (Chimera ID 61) is defined in
[`scripts/model.py`](scripts/model.py).

This case reproduces the five-variable example in the
[ESREL2026 article](https://research.tudelft.nl/en/publications/recent-experience-with-the-use-of-chimera-for-vine-copula-modelli/).

### Generating configuration

The generating families, parameters and structure are given by the following
three arrays. In $C_M$ and $\theta_M$, row $t$ lists the bicopulas of tree $t$,
and entries run from edge 1 to edge $5-t$ in `pyvinecopulib` order.
All rotations are zero. Parameters are Clayton θ or Gaussian correlation ρ,
as applicable; these are generating values, not fitted estimates.

$$
C_M = \left(\begin{array}{llll}
\mathrm{Clayton} & \mathrm{Clayton} & \mathrm{Clayton} & \mathrm{Clayton} \\
\mathrm{Clayton} & \mathrm{Clayton} & \mathrm{Clayton} &  \\
\mathrm{Clayton} & \mathrm{Clayton} &  &  \\
\mathrm{Clayton} &  &  &
\end{array}\right)
$$

$$
\theta_M = \left(\begin{array}{llll}
3.1819 & 3.1819 & 3.1819 & 3.1819 \\
3.1819 & 3.1819 & 3.1819 &  \\
3.1819 & 3.1819 &  &  \\
3.1819 &  &  &
\end{array}\right)
$$

$$
M = \left(\begin{array}{lllll}
4 & 2 & 4 & 5 & 5 \\
2 & 4 & 5 & 4 &  \\
1 & 5 & 2 &  &  \\
5 & 1 &  &  &  \\
3 &  &  &  &
\end{array}\right)
$$

The structure $M$ is Chimera ID 61, shared by both validation cases, in the
anti-diagonal convention passed to `pyvinecopulib.Vinecop.from_structure`.
Variable labels are 1–5. Blank entries in $M$ are unused zeros; the
anti-diagonal runs from the bottom left to the top right. All three arrays
have rows aligned to the left, with progressively fewer entries.
The source obtains $M$ by reversing the columns of its displayed
upper-triangular array.

The executable definition is [`scripts/model.py`](scripts/model.py).
Simulation streams are derived from the master seed and iteration using
`numpy.random.SeedSequence`, independently of job execution order.

### Fitting and comparison

**Both methods fit all 480 matrices to every dataset: 48,000 fits per method,
forming 48,000 paired AIC comparisons (100 × 480).** Each pair uses the same
dataset and candidate structure, fitted once by Trasgu and once by a manual
sequential Python loop. Trasgu reads Chimera in Zarr; the manual loop reads
the original TU Delft files. Both use identical observations and fitting controls.

The generating families in $C_M$ define the simulated data. During
exhaustive fitting and Dißmann selection, candidate families come from
`pyvinecopulib.one_par`, with AIC family selection and maximum likelihood
parameter estimation; they are not restricted to the generating assignment.
The additional fixed-model reference retains the generating structure and
families and re-estimates their parameters.

## Run

From the repository root, after `uv sync --frozen --extra benchmarks`:

```bash
uv run --no-sync python validation/esrel/run_validation.py --run-dir validation/esrel/runs/reproduce-full --iterations 100 --observations 300 --seed 20260928 --cores 4
```

Preparation downloads and verifies both catalogues. Add `--dry-run` to inspect
jobs; use `--iterations 1` in a separate directory for a pilot. Repeat the
command to resume; choose a new directory when changing settings or code.
Generated inputs, full fits and logs remain in `runs/`, outside Git.

## Results

**All 48,000 paired AICs agree** within `1e-5`; the maximum absolute difference
is **4.99981979374e-7**, consistent with Trasgu's six-decimal output.
Both methods reproduce the same exhaustive result within numerical tolerance.

- [Comparison table](results/aic_comparison.csv) and [summary](results/summary.json).
- [Figure](results/aic_differences.png): absolute AIC differences of exhaustive
  and Dißmann fits from the refitted generating model.
- [Reproducibility record](results/reproducibility.json): settings, versions,
  source hashes and input checksums.
