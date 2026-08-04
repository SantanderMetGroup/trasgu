#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 22:17:15 2023

@author: pmaresnasarre
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pyvinecopulib as pv


# Read data and prepare it independently of the current working directory.
experiment_dir = Path(__file__).resolve().parent
input_file = experiment_dir / "UI-1_ship_and_wake_data_for_TUDelft.csv"
output_file = experiment_dir / "unity_inbound.txt"

data = pd.read_csv(input_file, parse_dates=True).dropna().reset_index(drop=True)

cols = [3, 4, 7, 9, 21, 26, 29, 30]
selected_data = data.iloc[:, cols]
unity_inbound = pv.to_pseudo_obs(np.array(selected_data))

# Save pseudo-observations for Trasgu and the Dissmann comparison.
np.savetxt(output_file, unity_inbound)
