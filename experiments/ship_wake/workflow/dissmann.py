import numpy as np
import pyvinecopulib as pv

controls_dissmann = pv.FitControlsVinecop(
    family_set=pv.one_par,
    tree_criterion="tau",
    selection_criterion="aic",
    parametric_method="mle",
    show_trace=True,
)

samples = np.loadtxt("unity_inbound.txt")
dissman = pv.Vinecop.from_data(samples, controls=controls_dissmann)
print(dissman)
print(dissman.matrix)
print(dissman.aic())