# -*- coding: utf-8 -*-
# tests\rir_plot.py

# Copyright (c) 2025 Christos Sevastiadis
# License: GNU GPL v3.0
# Author: Christos Sevastiadis <csevast@auth.gr>

"""
    Provides plotting functions for the `scene_rir` package tests.

    This module provides the necessary plotting functions to be used by
    test scripts and notebooks.

"""

__author__ = "Christos Sevastiadis <csevast@ece.auth.gr>"

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from scene_rir.rir import ImpulseResponseSignal

_AXIS_LEVEL_BOTTOM = -100  # decibell
_AXIS_LEVEL_TOP = 0  # decibell
_TIME_VECTOR_START = 0  # second


def _set_ax_semilog_limits(ax: Axes, vec: np.ndarray) -> None:
    """Set the x-axis and y-axis limits for a axis plot."""

    lvlmax = np.max(vec)
    ax.set_xlim(left=10, right=100000)
    ax.set_ylim(lvlmax - 90, lvlmax + 10)


def plot_irs(signal: ImpulseResponseSignal) -> None:
    """Plot IR signals for testing."""

    smprte, irssglvec = signal.signal_vector()
    _, ax = plt.subplots(nrows=3, ncols=2)
    sglvec = signal._refsglvec
    sglsze = sglvec.size
    sgldur = sglsze / smprte
    tmevec = np.linspace(start=0, stop=sgldur, num=sglsze)
    ax[0, 0].plot(tmevec, sglvec)
    ax[0, 0].set_xlim(left=0, right=sgldur)

    sglvec = signal._recsglvec
    sglsze = sglvec.size
    sgldur = sglsze / smprte
    tmevec = np.linspace(start=0, stop=sgldur, num=sglsze)
    ax[1, 0].plot(tmevec, sglvec)
    ax[1, 0].set_xlim(left=0, right=sgldur)

    sglvec = irssglvec
    sglsze = sglvec.size
    sgldur = sglsze / smprte
    tmevec = np.linspace(start=0, stop=sgldur, num=sglsze)
    ax[2, 0].plot(tmevec, sglvec)
    ax[2, 0].set_xlim(left=0, right=sgldur)
    ax[2, 0].set_ylim(bottom=-1, top=1)

    sglspc = np.abs(signal._refspc)
    frqvec = np.linspace(start=1, stop=smprte, num=sglspc.size)
    frqvec = frqvec[: int(frqvec.size / 2)]
    sgllvlspc = 10 * np.log10(sglspc[: int(sglspc.size / 2)] ** 2)
    ax[0, 1].semilogx(frqvec, sgllvlspc)
    _set_ax_semilog_limits(ax[0, 1], sgllvlspc)

    sglspc = np.abs(signal._recspc)
    frqvec = np.linspace(start=1, stop=smprte, num=sglspc.size)
    frqvec = frqvec[: int(frqvec.size / 2)]
    sgllvlspc = 10 * np.log10(sglspc[: int(sglspc.size / 2)] ** 2)
    ax[1, 1].semilogx(frqvec, sgllvlspc)
    _set_ax_semilog_limits(ax[1, 1], sgllvlspc)

    sglspc = np.abs(signal._irsspc)
    frqvec = np.linspace(start=1, stop=smprte, num=sglspc.size)
    frqvec = frqvec[: int(frqvec.size / 2)]
    sgllvlspc = 10 * np.log10(sglspc[: int(sglspc.size / 2)] ** 2)
    ax[2, 1].semilogx(frqvec, sgllvlspc)
    _set_ax_semilog_limits(ax[2, 1], sgllvlspc)

    plt.show()


def plot_irs_deconvolution(signal: ImpulseResponseSignal) -> None:
    """Plot IR signals for testing."""

    smprte, irssglvec = signal.signal_vector()
    _, ax = plt.subplots(nrows=1, ncols=2)
    sglvec = signal._refsglvec
    sglsze = sglvec.size
    sgldur = sglsze / smprte
    tmevec = np.linspace(start=0, stop=sgldur, num=sglsze)
    ax[0].plot(tmevec, sglvec)
    ax[0].set_xlim(left=0, right=sgldur)
    sglspc = np.abs(signal._refspc)
    frqvec = np.linspace(start=1, stop=smprte, num=sglspc.size)
    frqvec = frqvec[: int(frqvec.size / 2)]
    sgllvlspc = 10 * np.log10(sglspc[: int(sglspc.size / 2)] ** 2)
    ax[1].semilogx(frqvec, sgllvlspc)
    _set_ax_semilog_limits(ax[1], sgllvlspc)

    _, ax = plt.subplots(nrows=1, ncols=2)
    sglvec = signal._invrefvec
    sglsze = sglvec.size
    sgldur = sglsze / smprte
    tmevec = np.linspace(start=0, stop=sgldur, num=sglsze)
    ax[0].plot(tmevec, sglvec)
    ax[0].set_xlim(left=0, right=sgldur)

    sglspc = np.abs(signal._invrefspc)
    frqvec = np.linspace(start=1, stop=smprte, num=sglspc.size)
    frqvec = frqvec[: int(frqvec.size / 2)]
    sgllvlspc = 10 * np.log10(sglspc[: int(sglspc.size / 2)] ** 2)
    ax[1].semilogx(frqvec, sgllvlspc)
    _set_ax_semilog_limits(ax[1], sgllvlspc)

    _, ax = plt.subplots(nrows=1, ncols=2)
    sglvec = irssglvec
    sglsze = sglvec.size
    sgldur = sglsze / smprte
    tmevec = np.linspace(start=0, stop=sgldur, num=sglsze)
    ax[0].plot(tmevec, sglvec)
    ax[0].set_xlim(left=0, right=sgldur)
    ax[0].set_ylim(bottom=-1, top=1)

    sglspc = np.abs(signal._irsspc)
    frqvec = np.linspace(start=1, stop=smprte, num=sglspc.size)
    frqvec = frqvec[: int(frqvec.size / 2)]
    sgllvlspc = 10 * np.log10(sglspc[: int(sglspc.size / 2)] ** 2)
    ax[1].semilogx(frqvec, sgllvlspc)
    _set_ax_semilog_limits(ax[1], sgllvlspc)

    plt.show()


def plot_irs_impulse(
    signal: ImpulseResponseSignal, deldur: float, sgllvl: float
) -> None:
    """Plot IR signals for testing."""

    smprte, irssglvec = signal.signal_vector()
    irssglvec[irssglvec == 0] = 10**-10
    irssgllvlvec = 10 * np.log10(irssglvec**2)
    sgldur = irssglvec.size / smprte
    tmevec = np.linspace(_TIME_VECTOR_START, sgldur, irssglvec.size)
    _, ax = plt.subplots()
    ax.set_ylim(_AXIS_LEVEL_BOTTOM, _AXIS_LEVEL_TOP)
    ax.set_xlim(-0.1, sgldur)
    ax.axvline(deldur, color="red")
    ax.axhline(sgllvl, color="yellow")
    ax.plot(tmevec, irssgllvlvec)
    _, ax = plt.subplots()
    ax.set_xlim(-0.1, sgldur)
    ax.axvline(deldur, color="red")
    ax.axhline(10 ** (sgllvl / 20), color="yellow")
    ax.plot(tmevec, irssglvec)

    plt.show()
