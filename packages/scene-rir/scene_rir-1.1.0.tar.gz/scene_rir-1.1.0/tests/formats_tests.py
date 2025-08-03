# -*- coding: utf-8 -*-
# tests\other_signals_tests.py

# Copyright (c) 2025 Christos Sevastiadis
# License: GNU GPL v3.0
# Author: Christos Sevastiadis <csevast@auth.gr>

"""
    Module for the testing of the `scene_rir` package, saving all WAV formats.

    This module tests the `scene_rir.rir` module. It saves the default excitation
    signal in all the available encoding formats (only different sample data type).

    Usage:
    ```>python.exe test_formats.py```

    or
    ```>python3 test_formats.py```

"""

__author__ = "Christos Sevastiadis <csevast@ece.auth.gr>"

import scene_rir.rir as rir
import scipy as sp

formats = [None, "uint8", "int16", "int32", "float32", "float64"]
signal = rir.SweptSineSignal()
for f in formats:
    signal.save(f"output/ss-signal-{f}.wav", f)
    filename = f"output/ss-signal-{f}.wav"
    smprte, sglvec = sp.io.wavfile.read(filename)
    print(f"File: {filename}, Data type: {sglvec.dtype}")
