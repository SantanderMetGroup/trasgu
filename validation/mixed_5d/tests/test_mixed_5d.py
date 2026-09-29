"""Check the specified generating model and independent implementation agreement."""

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from validation._shared.comparison import compare_fits, load_fits
from validation.mixed_5d.scripts.model import (
    FAMILIES,
    MATRIX,
    PARAMETERS,
    generating_model,
    simulate,
)
from validation.mixed_5d.scripts.compare_results import compare_iteration


def write_fits(directory, canonical, manual=None):
    directory.mkdir(parents=True, exist_ok=True)
    if manual is None:
        manual = canonical
    for filename, columns, values in (
        ("fit_iteration_1.csv", ["vine_id", "aic"], canonical),
        ("manual_fits_1.csv", ["manual_vine_id", "manual_aic"], manual),
    ):
        with (directory / filename).open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            writer.writerows(enumerate(values))


def test_exact_matrix_families_parameters_and_rotations():
    import pyvinecopulib as pv

    model = generating_model()
    expected = np.array(
        [
            [4, 2, 4, 5, 5],
            [2, 4, 5, 4, 0],
            [1, 5, 2, 0, 0],
            [5, 1, 0, 0, 0],
            [3, 0, 0, 0, 0],
        ]
    )
    np.testing.assert_array_equal(model.matrix, expected)
    np.testing.assert_array_equal(MATRIX, expected)
    assert sum(name == "clayton" for tree in FAMILIES for name in tree) == 6
    assert sum(name == "gaussian" for tree in FAMILIES for name in tree) == 4
    for t, tree in enumerate(FAMILIES):
        for e, name in enumerate(tree):
            bicop = model.get_pair_copula(t, e)
            assert bicop.family == getattr(pv.BicopFamily, name)
            assert bicop.rotation == 0
            np.testing.assert_array_equal(bicop.parameters, [[PARAMETERS[name]]])


def test_seeded_simulations_are_deterministic_and_distinct():
    first, seeds = simulate(300, 20260929, 1)
    again, repeated_seeds = simulate(300, 20260929, 1)
    other, _ = simulate(300, 20260929, 2)
    np.testing.assert_array_equal(first, again)
    assert seeds == repeated_seeds
    assert first.shape == (300, 5)
    assert np.all((first > 0) & (first < 1))
    assert not np.array_equal(first, other)


def test_mapping_rounding_and_tied_best_ids(tmp_path):
    values = np.arange(480, dtype=float)
    values[0] = 0.0000004
    values[1] = 0.0000001
    permutation = np.random.default_rng(9).permutation(480)
    mapping = np.argsort(permutation).tolist()
    manual = values[permutation]
    write_fits(tmp_path, values.round(6), manual)
    row = compare_iteration(tmp_path, 1, mapping)
    assert row["trasgu_vine_id"] == 0
    assert row["manual_best_chimera_id"] == 1
    assert row["same_selected_structure"] is False
    assert row["best_fit_agrees_within_tolerance"] is True
    manual[0] += 1
    with pytest.raises(ValueError, match="AIC mismatch"):
        compare_fits(values, manual, mapping)


@pytest.mark.parametrize("values", [np.arange(479), np.r_[np.nan, np.arange(479)]])
def test_missing_or_nonfinite_fit_fails(tmp_path, values):
    write_fits(tmp_path, values)
    with pytest.raises(ValueError):
        load_fits(tmp_path / "fit_iteration_1.csv", "vine_id", "aic")


def test_duplicate_matrix_id_fails(tmp_path):
    path = tmp_path / "fits.csv"
    path.write_text("vine_id,aic\n" + "0,-1\n" * 480)
    with pytest.raises(ValueError, match="exactly once"):
        load_fits(path, "vine_id", "aic")


def test_report_serialization_and_input_integrity(tmp_path):
    directory = tmp_path / "simulations/iteration_1"
    write_fits(directory, np.arange(480, dtype=float))
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "manifest.json").write_text(
        json.dumps(
            {"canonical_to_manual": list(range(480)), "generating_matrix_id": 61}
        )
    )
    (directory / "reference_fits_1.yaml").write_text(
        "aic_dissmann: 2.0\naic_fixed_matrix_clayton: 1.0\naic_ground_truth: 3.0\n"
    )
    data = directory / "vinecop_samples.txt"
    data.write_text("0.1 0.2 0.3 0.4 0.5\n")
    (directory / "simulation.json").write_text(
        json.dumps(
            {
                "iteration": 1,
                "data_sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
            }
        )
    )
    command = [
        sys.executable,
        "-m",
        "validation.mixed_5d.scripts.compare_results",
        str(tmp_path),
        "--iterations",
        "1",
    ]
    subprocess.run(command, check=True, capture_output=True)
    result = json.loads((tmp_path / "results/summary.json").read_text())
    assert result["matrix_comparisons"] == 480
    assert result["all_matrix_comparisons_passed"]
    assert result["best_fits_agree_including_ties"] == 1
    with (tmp_path / "results/aic_comparison.csv").open() as stream:
        columns = next(csv.reader(stream))
    reference = Path(__file__).resolve().parents[2] / "esrel/results/aic_comparison.csv"
    with reference.open() as stream:
        assert columns == next(csv.reader(stream))
    data.write_text("changed data\n")
    failed = subprocess.run(command, capture_output=True, text=True)
    assert failed.returncode != 0
    assert "input does not match" in failed.stderr


def test_reference_refit_preserves_mixed_model():
    from validation.mixed_5d.scripts.fit_reference_models import fit_references

    data, _ = simulate(300, 20260929, 1)
    result = fit_references(data)
    fixed = result["fixed_reference"]
    assert fixed["matrix"] == MATRIX.tolist()
    assert fixed["families"] == FAMILIES
    assert all(rotation == 0 for tree in fixed["rotations"] for rotation in tree)
    assert np.isfinite(
        [
            result[key]
            for key in ("aic_dissmann", "aic_fixed_matrix_clayton", "aic_ground_truth")
        ]
    ).all()
    assert any(
        fixed["parameters"][t][e][0][0] != PARAMETERS[family]
        for t, tree in enumerate(FAMILIES)
        for e, family in enumerate(tree)
    )
