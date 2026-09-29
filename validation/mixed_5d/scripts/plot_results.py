"""Plot mixed-family absolute AIC differences from the refitted generating structure."""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

from validation._shared.comparison import load_fits

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE.parent / "results" / "aic_comparison.csv"
STYLE_FILE = HERE.parents[2] / "styles" / "trasgu.mplstyle"


def load_comparison(source):
    """Read a comparison table or derive its plotting columns from a full run."""
    source = Path(source)
    if source.is_dir():
        directories = sorted(
            (source / "simulations").glob("iteration_*"),
            key=lambda path: int(path.name.removeprefix("iteration_")),
        )
        rows = []
        for directory in directories:
            iteration = int(directory.name.removeprefix("iteration_"))
            fitted = load_fits(
                directory / f"fit_iteration_{iteration}.csv", "vine_id", "aic"
            )
            references = yaml.safe_load(
                (directory / f"reference_fits_{iteration}.yaml").read_text()
            )
            rows.append(
                {
                    "iteration": iteration,
                    "aic_vine": float(np.min(fitted)),
                    "aic_dissmann": references["aic_dissmann"],
                    "aic_fixed_matrix_clayton": references["aic_fixed_matrix_clayton"],
                }
            )
        # Do not silently plot only a subset of a recorded experiment.
        provenance = source / "provenance.json"
        if provenance.exists():
            import json

            expected = json.loads(provenance.read_text())["config"]["iterations"]
            if [row["iteration"] for row in rows] != list(range(1, expected + 1)):
                raise ValueError(
                    f"{source}: expected all {expected} simulation directories"
                )
    else:
        with source.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"{source} contains no comparison rows")
    return rows


def aic_differences(rows):
    """Both methods use the same refitted fixed-generating-model baseline."""
    baseline = np.array([float(row["aic_fixed_matrix_clayton"]) for row in rows])
    differences = {}
    for label, column in (
        ("Exhaustive search", "aic_vine"),
        ("Dissmann algorithm", "aic_dissmann"),
    ):
        values = np.array([float(row[column]) for row in rows])
        if not np.isfinite(values).all() or not np.isfinite(baseline).all():
            raise ValueError("Non-finite AIC values")
        differences[label] = np.abs(values - baseline)
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help="comparison CSV or completed run directory (default: reference CSV)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="one output file; omitted: write PNG, PDF and SVG next to the comparison table",
    )
    args = parser.parse_args()
    differences = aic_differences(load_comparison(args.input))
    plt.style.use(STYLE_FILE)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for (label, difference), marker in zip(differences.items(), ("o", "x")):
        x = np.sort(difference)
        y = np.arange(1, len(x) + 1) / len(x)
        ax.plot(
            x, y, linestyle="none", marker=marker, markerfacecolor="none", label=label
        )
    ax.axvline(0, color="0.45", linestyle="--", linewidth=1)
    ax.set(
        xlabel="AIC difference from the fixed generating structure",
        ylabel="Cumulative proportion of simulations",
    )
    ax.legend()
    fig.tight_layout()
    destination = args.input / "results" if args.input.is_dir() else args.input.parent
    outputs = (
        [args.output]
        if args.output
        else [
            destination / f"aic_differences.{extension}"
            for extension in ("png", "pdf", "svg")
        ]
    )
    for output in outputs:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output)
        print(output)
    plt.close(fig)


if __name__ == "__main__":
    main()
