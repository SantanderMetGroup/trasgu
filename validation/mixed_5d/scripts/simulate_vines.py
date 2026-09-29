"""Generate one reproducible mixed-family dataset and its local Trasgu configuration."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import yaml

from validation.mixed_5d.scripts.model import simulate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--iteration", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--observations", type=int, default=300)
    parser.add_argument("--chimera", type=Path, required=True)
    args = parser.parse_args()
    if args.iteration < 1 or args.seed < 0 or args.observations < 2:
        parser.error("iteration >= 1, seed >= 0 and observations >= 2 are required")
    data, seeds = simulate(args.observations, args.seed, args.iteration)
    args.output.mkdir(parents=True, exist_ok=True)
    data_path = args.output / "vinecop_samples.txt"
    np.savetxt(data_path, data)
    template = Path(__file__).resolve().parents[1] / "config" / "trasgu.yaml"
    config = yaml.safe_load(template.read_text())
    config["chimera_url"] = str(args.chimera.resolve())
    (args.output / "trasgu.yaml").write_text(yaml.safe_dump(config))
    (args.output / "simulation.json").write_text(
        json.dumps(
            {
                "iteration": args.iteration,
                "seed": args.seed,
                "seeds": seeds,
                "observations": args.observations,
                "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
