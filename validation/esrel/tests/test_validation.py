"""Scientific invariants and failure checks for the ESREL workflow."""

import csv
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from compare_results import AIC_TOLERANCE, compare_fits, load_fits
from model import MATRIX, generating_model, simulate
from prepare_matrices import matrix_mapping


def test_seed_reproducibility_and_independence():
    first, seeds = simulate(20, 42, 1)
    repeated, repeated_seeds = simulate(20, 42, 1)
    second, _ = simulate(20, 42, 2)
    np.testing.assert_array_equal(first, repeated)
    assert seeds == repeated_seeds
    assert not np.array_equal(first, second)
    assert first.shape == (20, 5)
    assert np.all((first > 0) & (first < 1))
    np.testing.assert_array_equal(generating_model().matrix, MATRIX)


def test_comparison_aligns_ids_and_allows_csv_rounding():
    values = np.linspace(-1000.1234567, -10.7654321, 480)
    permutation = np.random.default_rng(42).permutation(480)
    manual = values[permutation]
    inverse = np.argsort(permutation)
    assert compare_fits(values.round(6), manual, inverse) < AIC_TOLERANCE
    manual[10] += 0.01
    with pytest.raises(ValueError, match="AIC mismatch"):
        compare_fits(values, manual, inverse)


@pytest.mark.parametrize("ids", [list(range(479)), [0] * 480, list(range(1, 481))])
def test_incomplete_or_duplicate_coverage_fails(tmp_path, ids):
    path = tmp_path / "fits.csv"
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["vine_id", "aic"])
        writer.writerows((i, -10.0) for i in ids)
    with pytest.raises(ValueError, match="exactly once"):
        load_fits(path, "vine_id", "aic")


def test_nonfinite_aic_fails(tmp_path):
    path = tmp_path / "fits.csv"
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["vine_id", "aic"])
        writer.writerows((i, "nan" if i == 200 else -10) for i in range(480))
    with pytest.raises(ValueError, match="non-finite"):
        load_fits(path, "vine_id", "aic")


def test_incomplete_catalogue_fails():
    with pytest.raises(ValueError, match="480 matrices"):
        matrix_mapping(np.array([MATRIX]), np.array([MATRIX]))


def test_report_serializes_and_counts_results(tmp_path, monkeypatch):
    import json
    import sys
    import yaml
    from compare_results import main

    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "manifest.json").write_text(
        json.dumps(
            {
                "canonical_to_manual": list(range(480)),
                "generating_matrix_id": 0,
            }
        )
    )
    directory = tmp_path / "simulations" / "iteration_1"
    directory.mkdir(parents=True)
    for filename, columns in (
        ("fit_iteration_1.csv", ["vine_id", "aic"]),
        ("manual_fits_1.csv", ["manual_vine_id", "manual_aic"]),
    ):
        with (directory / filename).open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            writer.writerows((i, -1000 + i) for i in range(480))
    (directory / "reference_fits_1.yaml").write_text(
        yaml.safe_dump(
            {
                "aic_dissmann": -900,
                "aic_fixed_matrix_clayton": -1001,
                "aic_ground_truth": -999,
            }
        )
    )
    monkeypatch.setattr(
        sys, "argv", ["compare_results.py", str(tmp_path), "--iterations", "1"]
    )
    main()
    summary = json.loads((tmp_path / "results" / "summary.json").read_text())
    assert summary["matrix_comparisons"] == 480
    assert summary["generating_matrix_selected_including_ties"] == 1
    assert summary["exhaustive_better_than_dissmann"] == 1


def test_plot_uses_absolute_differences_from_shared_fitted_baseline():
    from plot_results import aic_differences

    rows = [
        {
            "aic_vine": -100,
            "aic_dissmann": -80,
            "aic_fixed_matrix_clayton": -110,
            "aic_ground_truth": -200,
        },
        {
            "aic_vine": -150,
            "aic_dissmann": -130,
            "aic_fixed_matrix_clayton": -140,
            "aic_ground_truth": -300,
        },
    ]
    differences = aic_differences(rows)
    np.testing.assert_array_equal(differences["Exhaustive search"], [10, 10])
    np.testing.assert_array_equal(differences["Dissmann algorithm"], [30, 10])
    rows[0]["aic_dissmann"] = float("nan")
    with pytest.raises(ValueError, match="Non-finite"):
        aic_differences(rows)


def test_plot_reads_minimum_trasgu_aic_and_rejects_incomplete_run(tmp_path):
    import json
    import yaml
    from plot_results import load_comparison

    directory = tmp_path / "simulations" / "iteration_1"
    directory.mkdir(parents=True)
    with (directory / "fit_iteration_1.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["vine_id", "aic"])
        writer.writerows((i, -1000 - i) for i in range(480))
    (directory / "reference_fits_1.yaml").write_text(
        yaml.safe_dump(
            {
                "aic_dissmann": -900,
                "aic_fixed_matrix_clayton": -1500,
            }
        )
    )
    rows = load_comparison(tmp_path)
    assert rows == [
        {
            "iteration": 1,
            "aic_vine": -1479,
            "aic_dissmann": -900,
            "aic_fixed_matrix_clayton": -1500,
        }
    ]
    (tmp_path / "provenance.json").write_text(json.dumps({"config": {"iterations": 2}}))
    with pytest.raises(ValueError, match="expected all 2"):
        load_comparison(tmp_path)
