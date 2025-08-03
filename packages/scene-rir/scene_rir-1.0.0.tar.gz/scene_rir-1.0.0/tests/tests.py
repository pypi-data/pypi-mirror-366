# -*- coding: utf-8 -*-
# tests\tests.py

# Copyright (c) 2025 Christos Sevastiadis
# License: GNU GPL v3.0
# Author: Christos Sevastiadis <csevast@auth.gr>

"""
    Module for the testing of the `scene_rir` package.

    This module tests the `scene_rir.rir` module. It uses the generated
    excitation signals, as both reference and recorder response signals,
    producing Kronecker Delta responses, with or without delay.
    The output results are plotted in diagrams.

    Usage:
    ```>python.exe tests.py```
    
    or
    ```>python3 tests.py```

"""

__author__ = "Christos Sevastiadis <csevast@ece.auth.gr>"

import shutil

import numpy as np
import rir_plot
import scene_rir
import scipy as sp
from scene_rir import rir

#######################################################################

help(scene_rir)

#######################################################################

help(rir)

#######################################################################

shutil.os.mkdir("input")

DELAY_DURATION = 0
SIGNAL_LEVEL = -3

signal = rir.SweptSineSignal()
signal.save("output/ss-signal-00.wav")

shutil.copy("output/ss-signal-00.wav", "input/rec-signal-00.wav")
shutil.copy("output/ss-signal-00.wav", "input/ref-signal-00.wav")

params = {
    "rec_path": "input/rec-signal-00.wav",
    "ref_path": "input/ref-signal-00.wav",
    "sgllvl": SIGNAL_LEVEL,
}
irs_signal = rir.ImpulseResponseSignal(params)
irs_signal.save("output/irs-signal-00.wav")

rir_plot.plot_irs(irs_signal)
rir_plot.plot_irs_deconvolution(irs_signal)
rir_plot.plot_irs_impulse(irs_signal, DELAY_DURATION, SIGNAL_LEVEL)

#######################################################################

DELAY_DURATION = 0.5
SIGNAL_LEVEL = -3

signal = rir.SweptSineSignal()
signal.save("output/ss-signal-01.wav")

(smprte, sglvec) = signal.signal_vector()
slcvec = np.zeros(int(DELAY_DURATION * smprte))
sglvec = np.concatenate((slcvec, sglvec))
sp.io.wavfile.write("input/rec-signal-01.wav", smprte, sglvec)
shutil.copy("output/ss-signal-01.wav", "input/ref-signal-01.wav")

params = {
    "rec_path": "input/rec-signal-01.wav",
    "ref_path": "input/ref-signal-01.wav",
    "sgllvl": SIGNAL_LEVEL,
}
irs_signal = rir.ImpulseResponseSignal(params)
irs_signal.save("output/irs-signal-01.wav")

rir_plot.plot_irs(irs_signal)
rir_plot.plot_irs_deconvolution(irs_signal)
rir_plot.plot_irs_impulse(irs_signal, DELAY_DURATION, SIGNAL_LEVEL)

#######################################################################

DELAY_DURATION = 0
SIGNAL_LEVEL = -3

params = {
    "antslcdur": 0.3,
    "pstslcdur": 0.3,
}
signal = rir.SweptSineSignal(params)
signal.save("output/ss-signal-02.wav")

shutil.copy("output/ss-signal-02.wav", "input/rec-signal-02.wav")
shutil.copy("output/ss-signal-02.wav", "input/ref-signal-02.wav")

params = {
    "rec_path": "input/rec-signal-02.wav",
    "ref_path": "input/ref-signal-02.wav",
}
irs_signal = rir.ImpulseResponseSignal(params)
irs_signal.save("output/irs-signal-02.wav")

rir_plot.plot_irs(irs_signal)
rir_plot.plot_irs_deconvolution(irs_signal)
rir_plot.plot_irs_impulse(irs_signal, DELAY_DURATION, SIGNAL_LEVEL)

#######################################################################

DELAY_DURATION = 0.5
SIGNAL_LEVEL = -3

params = {
    "antslcdur": 0.3,
    "pstslcdur": 0.3,
}
signal = rir.SweptSineSignal(params)
signal.save("output/ss-signal-03.wav")

(smprte, sglvec) = signal.signal_vector()
slcvec = np.zeros(int(DELAY_DURATION * smprte))
sglvec = np.concatenate((slcvec, sglvec))
sp.io.wavfile.write("input/rec-signal-03.wav", smprte, sglvec)
shutil.copy("output/ss-signal-03.wav", "input/ref-signal-03.wav")

params = {
    "rec_path": "input/rec-signal-03.wav",
    "ref_path": "input/ref-signal-03.wav",
}
irs_signal = rir.ImpulseResponseSignal(params)
irs_signal.save("output/irs-signal-03.wav")

rir_plot.plot_irs(irs_signal)
rir_plot.plot_irs_deconvolution(irs_signal)
rir_plot.plot_irs_impulse(irs_signal, DELAY_DURATION, SIGNAL_LEVEL)

#######################################################################

DELAY_DURATION = 0.5
SIGNAL_LEVEL = -3

params = {
    "antslcdur": 0.3,
    "pstslcdur": 0.3,
    "ss_rtetyp": "lin",
}
signal = rir.SweptSineSignal(params)
signal.save("output/ss-signal-04.wav")

(smprte, sglvec) = signal.signal_vector()
slcvec = np.zeros(int(DELAY_DURATION * smprte))
sglvec = np.concatenate((slcvec, sglvec))
sp.io.wavfile.write("input/rec-signal-04.wav", smprte, sglvec)
shutil.copy("output/ss-signal-04.wav", "input/ref-signal-04.wav")

params = {
    "rec_path": "input/rec-signal-04.wav",
    "ref_path": "input/ref-signal-04.wav",
    "ss_rtetyp": "lin",
}
irs_signal = rir.ImpulseResponseSignal(params)
irs_signal.save("output/irs-signal-04.wav")

rir_plot.plot_irs(irs_signal)
rir_plot.plot_irs_deconvolution(irs_signal)
rir_plot.plot_irs_impulse(irs_signal, DELAY_DURATION, SIGNAL_LEVEL)
