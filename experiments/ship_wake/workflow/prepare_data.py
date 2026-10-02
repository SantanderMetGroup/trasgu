#!/usr/bin/env python3
"""Prepare the eight ship-wake pseudo-observation columns from the source CSV."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pyvinecopulib as pv


def prepare(source, output):
    data = pd.read_csv(source, parse_dates=True).dropna().reset_index(drop=True)
    selected = data.iloc[:, [3, 4, 7, 9, 21, 26, 29, 30]].to_numpy()
    np.savetxt(output, pv.to_pseudo_obs(selected))
    print(f"Saved {len(selected)} observations and 8 variables to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    prepare(args.source, args.output)
