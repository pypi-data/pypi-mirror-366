# -*- coding: utf-8 -*-
# src\scene_rir\__init__.py

# Copyright (c) 2025 Christos Sevastiadis
# License: GNU GPL v3.0
# Author: Christos Sevastiadis <csevast@auth.gr>

"""
    Room Impulse Response extraction package.

    The purpose of this package is to extract the room impulse response (RIR) from the
    recorded response signal of a proper excitation signal. It is part of the Audio
    Simulation Module of the Horizon project SCENE.

    Modules:
    - rir: Provides the classes implementing swept-sine excitation signal creation and
        room impulse response extraction from a recorded response.

    Examples:
    Example of usage from command line (Windows OS):
    > python -m scene_rir
    Usage: python -m scene_rir [command] [parameter1] [parameter2]
    or
    python3 -m scene_rir [command] [parameter1] [parameter2]
    Available commands:
    save   Save the default swept-sine signal.

    > python -m scene_rir --help
    Usage: python -m scene_rir= [command] [parameter1] [parameter2]
    or
    python3 -m scene_rir [command] [parameter1] [parameter2]
    Available commands:
    save   Save the default swept-sine signal.

    > python -m scene_rir save my_folder/my_signal.wav

"""

__all__ = ["rir"]
__author__ = "Christos Sevastiadis <csevast@ece.auth.gr>"

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # for Python<3.8

__version__ = version(__name__)
