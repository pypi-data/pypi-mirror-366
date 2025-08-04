# -*- coding: utf-8 -*-
# tests\other_signals_tests.py

# Copyright (c) 2025 Christos Sevastiadis
# License: GNU GPL v3.0
# Author: Christos Sevastiadis <csevast@auth.gr>

"""
    Module for the testing of the `scene_rir` package, over the other signals.

    This module tests the `scene_rir.rir` module. It uses an excitation signal
    generated from another source, and extracts the room impulse responses from
    three recorded responses in real rooms. The output results are plotted in
    diagrams.

    Usage:
    ```>python.exe other_signals_tests.py```

    or
    ```>python3 other_signals_tests.py```

"""

__author__ = "Christos Sevastiadis <csevast@ece.auth.gr>"

import rir_plot
from scene_rir import rir

#######################################################################

params = {
    "frqstp": 22000,
    "frqstt": 10,
    "rec_path": "input-other/GrCLab1SSRPos2.wav",
    "ref_path": "input-other/Sweep(10-22000Hz,10s-0.2s).wav",
}
irs_signal = rir.ImpulseResponseSignal(params)
irs_signal.save("output-other/irs-signal-GrCLab1SSRPos2.wav")

rir_plot.plot_irs(irs_signal)
rir_plot.plot_irs_deconvolution(irs_signal)

#######################################################################

params = {
    "frqstp": 22000,
    "frqstt": 10,
    "rec_path": "input-other/GrCLab2SSRPos1Src1.wav",
    "ref_path": "input-other/Sweep(10-22000Hz,10s-0.2s).wav",
}
irs_signal = rir.ImpulseResponseSignal(params)
irs_signal.save("output-other/irs-signal-GrCLab2SSRPos1Src1.wav")

rir_plot.plot_irs(irs_signal)
rir_plot.plot_irs_deconvolution(irs_signal)

#######################################################################

params = {
    "frqstp": 22000,
    "frqstt": 10,
    "rec_path": "input-other/GrCLab2SSRPos1Src2.wav",
    "ref_path": "input-other/Sweep(10-22000Hz,10s-0.2s).wav",
}
irs_signal = rir.ImpulseResponseSignal(params)
irs_signal.save("output-other/irs-signal-GrCLab2SSRPos1Src2.wav")

rir_plot.plot_irs(irs_signal)
rir_plot.plot_irs_deconvolution(irs_signal)

#######################################################################
