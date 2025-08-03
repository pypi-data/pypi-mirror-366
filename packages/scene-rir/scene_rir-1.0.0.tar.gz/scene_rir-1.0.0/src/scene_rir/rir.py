# -*- coding: utf-8 -*-
# src\scene_rir\rir.py

# License: GNU GPL v3.0
# Copyright (c) 2025 Christos Sevastiadis
# Author: Christos Sevastiadis <csevast@auth.gr>

"""
    Room Impulse Response extraction package main module.

    Provides the classes implementing swept-sine excitation signal creation and room
    impulse response extraction from a recorded response.

    Examples:
    Example of usage from command line (Windows OS):

    > python -m scene_rir.rir
    Usage: python -m scene_rir.rir [command] [parameter1] [parameter2]
    or
    python3 -m scene_rir.rir [command] [parameter1] [parameter2]
    Available commands:
    save   Save the default swept-sine signal.

    > python -m scene_rir.rir --help
    Usage: python -m scene_rir.rir [command] [parameter1] [parameter2]
    or
    python3 -m scene_rir.rir [command] [parameter1] [parameter2]
    Available commands:
    save   Save the default swept-sine signal.

    > python -m scene_rir.rir save my_folder/my_signal.wav

"""

__all__ = ["ImpulseResponseSignal", "SweptSineSignal"]
__author__ = "Christos Sevastiadis <csevast@ece.auth.gr>"

import sys
from pathlib import Path

import numpy as np
import scipy as sp

# Vector with sampling rates, in samples per second, or Hz.
_SAMPLING_RATES = np.array([11025, 16000, 22050, 32000, 44100, 48000], dtype=np.uint32)

# Vector with signal sizes in samples, in steps of power of .two, for FFT calculation
# efficiency.
_SIGNAL_SIZES = np.array([2 ** (14 + i) for i in range(7)])

# Default peak level for any produced signal, in deciBel relative to full scale, dB FS.
_PEAK_LEVEL_FS = -3

_DEFAULT_OUTPUT_SUBFOLDER = "output"

_DEFAULT_INPUT_SUBFOLDER = "input"

_DEFAULT_SS_SIGNAL_FILENAME = "ss-signal.wav"

_DEFAULT_IRSSIGNAL_FILENAME = "irs-signal.wav"

_DEFAULT_INPUT_REFERENCE_FILENAME = "ref-signal.wav"

_DEFAULT_INPUT_RECORDING_FILENAME = "rec-signal.wav"

# Default start frequency of swept-sine, in hertz, Hz.
_DEFAULT_START_FREQUENCY = 20

# Default stop frequency of swept-sine, in hertz, Hz.
_DEFAULT_STOP_FREQUENCY = 20000

# Default ante swept-sine silence duration, in seconds, s.
_DEFAULT_ANTE_SILENCE_DURATION = 0

# Default post swept-sine silence duration, in seconds, s.
_DEFAULT_POST_SILENCE_DURATION = 0

_DEFAULT_SWEEP_AMPLITUDE_PEAK_VALUE = 1 / np.sqrt(2)

_NUMBER_OF_DIGITS = 7

_USAGE_STRING = """Usage: python -m scene_rir.rir [command] [path] [rec_path] [ref_path]
or
python3 -m scene_rir.rir [command] [path] [rec_path] [ref_path]
Available commands:
ss-save   Save the default swept-sine signal in the `path` file.
ir-save   Save the impulse response signal in the `path` file, calculated by
          recorder signal read from the `rec_path` file, and reference signal
          read from the `ref_path` file.
"""


class SweptSineSignal:
    """Swept-sine excitation signal production class.

    Attributes
    ----------

    smprte : int
        Sampling rate of the signal, in hertz (Hz) or samples per second, with default
        value 44100 Hz.
    sglsze : int
        Signal size, in samples, with default value 128 kibit.
    frqstt : float
        Start frequency of the swept-sine signal, in hertz (Hz), with default value 10
        Hz.
    frqstp : float
        Stop frequency of the swept-sine signal, in hertz (Hz), with default value
        20000 Hz.
    sgllvl : float
        Signal peak level, in decibel relative to full scale (dB FS), with default
        value -3 dB FS.
    antslcdur : float
        Ante swept-sine waveform silence duration, in seconds (s), with default
        value 0.01 s.
    pstslcdur : float
        Post swept-sine waveform silence duration, in seconds (s), with default
        value 0.01 s.
    ss_rtetyp : string
        Swept-sine increase rate of frequency in time, "log" for logarithmic, or
        "lin" for linear, with default value "log".

    """

    def __init__(self, par=None) -> None:
        """Initialize the class.

        Sampling rate index, smprteidx, signal size index, sglszeidx, combination
        table for sampling rate (Hz), smprte, signal size (samples), sglsze, and
        signal duration (s), sgldur.

                   sglszeidx       0       1       2       3       4       5       6
             sglsze, samples   16384   32768   65536  131072  262144  524288 1048576
        smprteidx smprte, Hz                       sgldur, s
                0      11025   1.486   2.972   5.944  11.889  23.777  47.554  95.109
                1      16000   1.024   2.048   4.096   8.192  16.384  32.768  65.536
                2      22050   0.743   1.486   2.972   5.944  11.889  23.777  47.554
                3      32000   0.512   1.024   2.048   4.096   8.192  16.384  32.768
                4      44100   0.372   0.743   1.486   2.972   5.944  11.889  23.777
                5      48000   0.341   0.683   1.365   2.731   5.461  10.923  21.845

        Parameters
        ----------
        par : dict
            An initialization parameters dictionary where:
            - "smprteidx" (int): Sample rate selection index, from 0 to 5, with default
                value 4, for 44100 Hz. Select a value from _SAMPLING_RATES ndarray,
                [11025, 16000, 22050, 32000, 44100, 48000], in hertz (Hz).
            - "sglszeidx" (int): Signal size selection index, from 0 to 6, with default
                value 3, for 128 kibit of signal samples, or 2.731 seconds of signal
                duration, when 44100 Hz (smprtidx = 4) sampling rate is defined.
                Select a value from _SIGNAL_SIZES ndarray, corresponding to [16, 32, 64,
                128, 255, 512, 1024] kibit signal samples, or corresponding to [0.372,
                0.743, 1.486, 2.972, 5.944, 11.889, 23.777] time duration, in seconds
                (s).
            - "frqstt" (int): Swept-sine start frequency, in hertz (Hz), with default
                value 20 Hz.
            - "frqstp" (int): Swept-sine stop frequency, in hertz (Hz), with default
                value 20000 Hz.
            - "sgllvl" (float): Signal peak level, in decibel relative to full scale
                (dB FS), with default value -3 dB FS."
            - "antslcdur" (float): Ante swept-sine waveform silence duration, in seconds
                (s), with default value 0.01 s.
            - "pstslcdur" (float): Post swept-sine waveform silence duration, in seconds
                (s), with default value 0.01 s.
            - "ss_rtetyp" (string): Swept-sine increase rate of frequency in time, "log"
                for logarithmic, or "lin" for linear, with default value "log".

        Examples
        --------
        Create and save the default exponential swept-sine excitation signal.

        >>> from scene_rir import rir
        >>>
        >>> signal = rir.SweptSineSignal()
        >>> signal.save("output/ss-signal-44100_kHz-2972_ms.wav")

        Usage example of creating and using a swept-sine signal in a Python script.
        >>> from matplotlib import pyplot as plt
        >>> from scene_rir import rir
        >>>
        >>> params = {
        ...     "antslcdur": 0.1,
        ...     "frqstp": 10000,
        ...     "frqstt": 100,
        ...     "pstslcdur": 0.1,
        ...     "sgllvl": -6,
        ...     "sglszeidx": 2,
        ...     "smprteidx": 5,
        ...     "ss_rtetyp": "log",
        ... }
        >>> signal = rir.SweptSineSignal(params)
        >>> _, sglvec = signal.signal_vector()
        >>> tmevec = signal.time_vector()
        >>> sgldur = signal.sgldur
        >>>
        >>> _, ax = plt.subplots()
        >>> ax.plot(tmevec, sglvec)
        [<matplotlib.lines.Line2D object at 0x000001A40B885330>]
        >>> ax.set_xlim(0, sgldur)
        (0.0, 1.3653333)
        >>> ax.set_ylim(-1, 1)
        (-1.0, 1.0)
        >>> plt.show()

        """

        if par is None:
            par = {}
        smprteidx = int(par["smprteidx"]) if "smprteidx" in par else 4
        if smprteidx < 0 or smprteidx > 5:
            raise ValueError(
                "Argument for the sampling rate index parameter, "
                "smprteidx, out of bounds, [0, 5]."
            )
        else:
            self.smprte = _SAMPLING_RATES[smprteidx]
        sglszeidx = int(par["sglszeidx"]) if "sglszeidx" in par else 3
        if sglszeidx < 0 or sglszeidx > 7:
            raise ValueError(
                "Argument for the fft size parameter, sglszeidx,"
                " out of bounds, [0, 7]."
            )
        else:
            self.sglsze = _SIGNAL_SIZES[sglszeidx]
        self.frqstt = par.get("frqstt", _DEFAULT_START_FREQUENCY)
        self.frqstp = int(par["frqstp"]) if "frqstp" in par else _DEFAULT_STOP_FREQUENCY
        if self.frqstt > self.smprte / 2 or self.frqstt > self.frqstp:
            raise ValueError(
                f"The argument {self.frqstt} for the sweep start frequency parameter, "
                f"frqstt, should not be higher than the half of the sampling frequency,"
                f" i.e. {self.smprte / 2} Hz, and higher than the argument for the "
                f"sweep stop frequency parameter, frqstp, i.e. {self.frqstp} Hz."
            )
        if self.frqstp < self.frqstt or self.frqstp > self.smprte / 2:
            raise ValueError(
                f"The argument {self.frqstp} for the sweep stop frequency parameter, "
                "frqstp, should not be lower than the arguement for the sweep start "
                f"parameter, frqstt, i.e. {self.frqstt} Hz, and higher than the half "
                f"of the sampling frequency, i.e. {self.smprte / 2} Hz."
            )
        self.sgllvl = par.get("sgllvl", _PEAK_LEVEL_FS)
        if self.sgllvl > 0:
            raise ValueError(
                "Argument for the signal level, sgllvl, should be negative"
                " or zero dB FS."
            )
        self.antslcdur = par.get("antslcdur", _DEFAULT_ANTE_SILENCE_DURATION)
        self.pstslcdur = (
            par["pstslcdur"] if "pstslcdur" in par else _DEFAULT_POST_SILENCE_DURATION
        )
        self.ss_rtetyp = par.get("ss_rtetyp", "log")
        if self.ss_rtetyp != "log" and self.ss_rtetyp != "lin":
            raise ValueError(
                "Argument for the sweep sine rate type parameter, ss_rtetyp,"
                " should be 'log', for logarithmic, or 'lin' for linear."
            )

        self.calculate_sgldur()

    def _print_help_table(self) -> None:
        """Print the table swept-sine signal parameters combinations."""

        print("           sglszeidx", end="")
        for k in range(7):
            print(f" {k:7d}", end="")
        print()

        print("     sglsze, samples", end="")
        for k in range(7):
            tmpparams = {
                "sglszeidx": k,
                "smprteidx": 4,
            }
            tmpsgl = SweptSineSignal(tmpparams)
            print(f" {tmpsgl.sglsze:7d}", end="")
        print()

        print("smprteidx smprte, Hz                       sgldur, s")
        for i in range(6):
            for k in range(7):
                tmpparams = {
                    "sglszeidx": k,
                    "smprteidx": i,
                }
                tmpsgl = SweptSineSignal(tmpparams)
                if k == 0:
                    print(f"{i:9d} {tmpsgl.smprte:10d}", end="")
                print(f" {tmpsgl.sgldur:7.3f}", end="")
            print()

    def calculate_sgldur(self) -> float:
        """Calculate the signal duration.

        Returns
        -------
        float
            The signal duration.

        """

        self.sgldur = round(self.sglsze / self.smprte, _NUMBER_OF_DIGITS)

        return self.sgldur

    def time_vector(self) -> int:
        """Generate the time vector of the signal.

        Returns
        -------
        ndarray
            A vector array corresponding to the signal time, in seconds.

        """

        self.calculate_sgldur()

        return np.linspace(0, self.sgldur, self.sglsze)

    def _frqfdelen(self, frqfde, smprte, swplen, fdetyp="") -> int:
        """
        Calculate the fade in/out length for the given frequency.

        Parameters
        ----------
        frqfde : float
            End or begin frequency of fade-in or fade-out, in hertz (Hz).
        smprte : float
            Sampling rate, in hertz (Hz) or samples per second.
        swplen : int
            Sweep length, in samples.

        Returns
        -------
        fdelen : int
            Fade length, in samples.

        """

        if fdetyp == "lin":
            return int(np.ceil(min(swplen / 10, max(smprte / frqfde**2, swplen / 200))))
        else:
            return int(np.ceil(min(swplen / 10, max(smprte / frqfde, swplen / 200))))

    def _iniswp(self, frqstt, frqstp, fftsze, smprte, typ="", antslcdur=0, pstslcdur=1):
        """
        Initialize sweep.

        Parameters
        ----------
            frqstt: float
                Start frequency, in hertz (Hz).
            frqstp : float
                Stop frequency, in hertz (Hz).
            fftsze : int
                FFT size, in samples.
            smprte : float
                Sampling time frequency, in hertz (Hz) or samples per second.
            typ : {'lin', 'log'}
                Sweep rate type, 'lin': Linear, 'log': Logarithmic.
            antslcdur : float
                Ante sweep silence duration, in seconds (s).
            pstslcdur : float
                Post sweep silence duration, in seconds (s).

        Returns
        -------
            frqsttcnd : float
                Conditioned start frequency, in hertz (Hz).
            swplen : int
                Number of sweep samples.
            swpdur : float
                Sweep duration, in seconds (s).
            antslclen : int
                Number of ante sweep silence duration samples.
            antfdelen : int
                Start group delay sample number.
            pstfdelen : int
                Number of post fade samples.

        """

        antslclen = int(np.ceil(antslcdur * smprte))
        pstslclen = int(np.ceil(pstslcdur * smprte))
        swplen = fftsze - antslclen - pstslclen
        swpdur = swplen / smprte
        frqsttcnd = int(np.ceil(max(frqstt, smprte / fftsze)))
        antfdelen = self._frqfdelen(frqsttcnd, smprte, swplen, fdetyp=typ)
        antfdelen = self._frqfdelen(frqsttcnd, smprte, swplen, fdetyp=typ)
        pstfdelen = self._frqfdelen(frqstp, smprte, swplen, fdetyp=typ)
        return frqsttcnd, swplen, swpdur, antslclen, antfdelen, pstfdelen

    def _cndswp(self, swpswf, swplen, antslclen, antfdelen, pstfdelen):
        """
        Condition a swept-sine signal, by fading in and out and adding silence.

        Parameters
        ----------
            swpswf : ndarray
                Swept-sine signal to be conditioned.
            swplen : int
                Swept-sine size, in samples.
            antslclen : int
                Ante silence size, in samples.
            antfdelen : int
                Ante fade size, in samples.
            pstfdelen : int
                Post fade size, in samples.

        Returns
        -------
            ndarray
                The conditioned swept-sine signal vector.

        """

        # Apply Hanning enveloping fade in of the swept-signal.
        wndstt = np.hanning(2 * antfdelen)
        swpswf[antslclen : (antslclen + antfdelen)] = (
            swpswf[antslclen : (antslclen + antfdelen)] * wndstt[:antfdelen]
        )
        # Apply Hanning enveloping fade out of the swept-signal.
        wndstp = np.hanning(2 * pstfdelen)
        swpswf[(antslclen + swplen - pstfdelen) : (antslclen + swplen)] = (
            swpswf[(antslclen + swplen - pstfdelen) : (antslclen + swplen)]
            * wndstp[pstfdelen:]
        )
        swpswf[(antslclen + swplen) :] = 0
        return swpswf

    def _ss_sgltme(
        self,
        frqstt,
        frqstp,
        fftsze,
        smprte,
        antslcdur,
        pstslcdur,
        swpapv=_DEFAULT_SWEEP_AMPLITUDE_PEAK_VALUE,
        typ="log",
    ):
        """
        Return a swept-sine signal in the time domain.

        Parameters
        ----------
            frqstt : float
                Sweep start frequency, in hertz (Hz).
            frqstp : float
                Sweep stop freqeuncy, in hertz (Hz).
            fftsze : int
                FFT size, in samples.
            smprte : float
                Sampling time frequency, in hertz (Hz) or samples per second.
            antslcdur : float
                Ante sweep silence duration, in seconds (s).
            pstslcdur : float
                Post sweep silence dura, in seconds (s).
            swpapv : float
                Sweep signal waveform amplitude peak value.
            typ : {'lin', 'log'}
                Sweep rate type, 'lin': Linear, 'log': Logarithmic, with default value
                "log".

        Returns
        -------
            ndarray
                The swept-sine signal vector.

        """

        self.calculate_sgldur()
        frqsttcnd, swplen, __, antslclen, antfdelen, pstfdelen = self._iniswp(
            frqstt, frqstp, fftsze, smprte, typ, antslcdur, pstslcdur
        )
        swppha = np.zeros(fftsze)
        if typ == "lin":
            # Angelo Farina approach
            swpdur = swplen / smprte
            tme = np.linspace(0, swpdur, swplen)
            pha = (
                2 * np.pi * frqsttcnd * tme
                + 2 * np.pi * (frqstp - frqsttcnd) / swpdur * tme**2 / 2
            )
            swppha[antslclen : antslclen + swplen] = pha
        elif typ == "log":
            # Angelo Farina approach
            swpdur = swplen / smprte
            tme = np.linspace(0, swpdur, swplen)
            pha = (
                2
                * np.pi
                * frqsttcnd
                * swpdur
                / np.log(frqstp / frqsttcnd)
                * (np.exp(tme / swpdur * np.log(frqstp / frqsttcnd)) - 1)
            )
            swppha[antslclen : (antslclen + swplen)] = pha
        return self._cndswp(
            swpapv * np.sin(swppha), swplen, antslclen, antfdelen, pstfdelen
        )

    def signal_vector(self) -> tuple[int, np.ndarray]:
        """Create and return the swept-sine signal vector.

        Returns
        -------
        int
            Sampling time frequency, in hertz (Hz) or samples per second.
        ndarray
            The swept-sine signal vector.

        """

        sglvec = self._ss_sgltme(
            self.frqstt,
            self.frqstp,
            self.sglsze,
            self.smprte,
            self.antslcdur,
            self.pstslcdur,
            10 ** (self.sgllvl / 20),
            self.ss_rtetyp,
        )

        return (self.smprte, sglvec)

    def save(self, /, path=None, format="int16") -> None:
        """Create and save the swept-sine signal in a WAV file.

        Parameters
        ----------
        path : string
            The filename path, for example "my_signal.wav" or
            "my_output/my_signal.wav". Default value is
            "./output/ss-signal.wav".
        format: string
            The samples data type for the encoding. One of "uint8", "int16", "int32",
            "float32", and "float64". Default value is "int16".

        """

        smprte, sglvec = self.signal_vector()
        p = (
            Path("./" + _DEFAULT_OUTPUT_SUBFOLDER + "/" + _DEFAULT_SS_SIGNAL_FILENAME)
            if path is None
            else Path(path)
        )
        d = p.parent
        if not d.exists():
            d.mkdir(parents=True)
        if format == "uint8":
            dattpe = np.uint8
        elif format == "int32":
            dattpe = np.int32
        elif format == "float32":
            dattpe = np.float32
        elif format == "float64":
            dattpe = np.float64
        else:
            dattpe = np.int16
        if np.issubdtype(dattpe, np.integer):
            amppk = np.iinfo(dattpe).max
            sglvec = amppk * sglvec
        sp.io.wavfile.write(p, smprte, sglvec.astype(dattpe))


class ImpulseResponseSignal:
    """Impulse response signal calculation class.

    Attributes
    ----------

    rec_path : string
        Path of the recorded input WAV file, with default value "input/rec-signal.wav".
    ref_path : string)
        Path of the reference input WAV file, with default value "input/ref-signal.wav".
    frqstt : float
        Start frequency of the swept-sine signal, in hertz (Hz), with default value 20
        Hz.
    frqstp : float
        Stop frequency of the swept-sine signal, in hertz (Hz), with default balue
        20000 Hz.
    sgllvl : float
        Signal peak level, in decibel relative to full scale (dB FS).
    ss_rtetyp : string
        Swept-sine increase rate of frequency in time, "log" for logarithmic, or
        "lin" for linear, with default value "log".

    """

    def __init__(self, par=None) -> None:
        """Initilize the class.

        Parameters
        ----------
        par : dict
            An initialization parameters dictionary where:
            - "rec_path" (string): Path of the recorded input WAV file.
            - "ref_path" (string): Path of the reference input WAV file.
            - "frqstt" (int): Swept-sine start frequency, in hertz (Hz), with default
                value 20 Hz.
            - "frqstp" (int): Swept-sine stop frequency, in hertz (Hz), with default
                value 20000 Hz.
            - "sgllvl" (float): Signal peak level, in decibel relative to full scale
                (dB FS).
            - "ss_rtetyp" (string): Swept-sine increase rate of frequency in time, "log"
                for logarithmic, or "lin" for linear, with default value "log".

        Examples
        --------
        Exctract the room impulse response from a recorded response signal to a
        previously produced swept-sine excitation signal.

        >>> from scene_rir import rir
        >>>
        >>> params = {
        ...     "rec_path": "input/rec-signal.wav",
        ...     "ref_path": "output/ref-signal.wav",
        ...     "sgllvl": 0,
        ... }
        >>> irs_signal = rir.ImpulseResponseSignal(params)
        >>> irs_signal.save("output/irs-signal.wav")

        Usage example of extracting the impulse response in a Python script.
        >>> import numpy as np
        >>> from matplotlib import pyplot as plt
        >>> from scene_rir import rir
        >>>
        >>> par = {
        ...     "rec_path": "input/rec-signal.wav",
        ...     "ref_path": "output/ref-signal.wav",
        ...     "path": "output/irs-signal.wav",
        ...     "sgllvl": 0,
        ... }
        >>> irs_signal = rir.ImpulseResponseSignal(par)
        >>> smprte, sglvec = irs_signal.signal_vector()
        >>>
        >>> _, ax = plt.subplots()
        >>>
        >>> sgldur = sglvec.size / smprte
        >>> tmevec = np.linspace(0, sgldur, sglvec.size)
        >>> ax.plot(tmevec, sglvec)
        [<matplotlib.lines.Line2D object at 0x000002D23FF9E1D0>]
        >>> ax.set_xlim(0, sgldur)
        (0.0, 2.972154195011338)
        >>>
        >>> plt.show()

        """

        if par is None:
            par = {}
        self.ref_path = par.get(
            "ref_path",
            "./" + _DEFAULT_INPUT_SUBFOLDER + "/" + _DEFAULT_INPUT_REFERENCE_FILENAME,
        )
        self.rec_path = par.get(
            "rec_path",
            "./" + _DEFAULT_INPUT_SUBFOLDER + "/" + _DEFAULT_INPUT_RECORDING_FILENAME,
        )
        self.frqstt = par.get("frqstt", _DEFAULT_START_FREQUENCY)
        self.frqstp = par.get("frqstp", _DEFAULT_STOP_FREQUENCY)
        if self.frqstt > self.frqstp:
            raise ValueError(
                f"The argument {self.frqstt} for the sweep start frequency parameter, "
                f"frqstt, should not be higher than the argument for the sweep stop "
                f"frequency parameter, frqstp, i.e. {self.frqstp} Hz."
            )
        if self.frqstp < self.frqstt:
            raise ValueError(
                f"The argument {self.frqstp} for the sweep stop frequency parameter, "
                "frqstp, should not be lower than the arguement for the sweep start "
                f"parameter, frqstt, i.e. {self.frqstt} Hz."
            )
        self.sgllvl = par.get("sgllvl", _PEAK_LEVEL_FS)
        if self.sgllvl > 0:
            raise ValueError(
                "Argument for the signal level, sgllvl, should be negative"
                " or zero dB FS."
            )
        self.ss_rtetyp = par.get("ss_rtetyp", "log")
        if self.ss_rtetyp != "log" and self.ss_rtetyp != "lin":
            raise ValueError(
                "Argument for the sweep sine rate type parameter, ss_rtetyp,"
                " should be 'log', for logarithmic, or 'lin' for linear."
            )

    def signal_vector(self) -> tuple[int, np.ndarray]:
        """Create and return the impulse response signal vector.

        Returns
        -------
        int
            Sampling time frequency, in hertz (Hz) or samples per second.
        ndarray
            The impulse response signal vector.

        """

        # Read the reference swept-sine signal from a WAV file.
        (smprte, self._refsglvec) = sp.io.wavfile.read(self.ref_path)
        # Read the recorded response signal from a WAV file.
        (recsmprte, self._recsglvec) = sp.io.wavfile.read(self.rec_path)
        # Test if the signals have the same sampling rate.
        if smprte != recsmprte:
            raise ValueError(
                "Error: Sampling rate should be the same for both reference signal and"
                " recorded signal wave files."
            )
        # Inverse in time the reference swept-sine signal
        invrefvec = np.flip(
            self._refsglvec if np.ndim(self._refsglvec) == 1 else self._refsglvec[:, 0]
        )
        if self.ss_rtetyp == "log":
            # Find where the swept-sine signal starts, after the ante swept-sine signal
            # silence.
            sttidx = 0
            stpidx = 0
            for i in range(self._refsglvec.size):
                if self._refsglvec[i] != 0:
                    sttidx = i - 1
                    if sttidx < 0:
                        sttidx = 0
                    break
            # Find where the post swept-sine signal silence starts, after stopping the
            # swept-sine.
            for i in range(self._refsglvec.size - 1, -1, -1):
                if self._refsglvec[i] != 0:
                    stpidx = i + 2
                    if stpidx > self._refsglvec.size:
                        stpidx = self._refsglvec.size
                    break
            # Calculate the size of the swept-sine signal, without the ante and post
            # silences.
            swplen = stpidx - sttidx
            # Calculate the duration in seconds, of the swept-sine signal, without
            # the silent ante and post parts.
            swpdur = swplen / smprte
            # Create the time vector of the swept-sine signal, in seconds.
            swptmevec = np.linspace(0, swpdur, swplen)
            # Calculate the the level envelope for the time-inversed swept-sine, of -3
            # dB
            # decrease per octave, starting from 0 dB, and endint to
            # -3*lb(frqstp/frqstt) dB.
            swpenvlvlvec = (
                swptmevec * (-6) * np.log2(self.frqstp / self.frqstt) / swpdur
            )
            # Calculate the factor vector of the envelope.
            swpenvvec = 10 ** (swpenvlvlvec / 20)
            # Find where the reversed in time swept-sine signal starts, after the
            # reversed post swept-sine signal silence.
            for i in range(invrefvec.size):
                if invrefvec[i] != 0:
                    sttidx = i - 1
                    if sttidx < 0:
                        sttidx = 0
                    break
            # Find where the reversed in time swept-sine signal stops, before the
            # reversed ante swept-sine signal silence.
            for i in range(invrefvec.size - 1, -1, -1):
                if invrefvec[i] != 0:
                    stpidx = i + 2
                    if stpidx > self._refsglvec.size:
                        stpidx = self._refsglvec.size
                    break
            # Apply the envelope over the swept-sine signal only.
            self._invrefvec = np.concatenate(
                (
                    np.zeros(sttidx),
                    invrefvec[sttidx:stpidx] * swpenvvec,
                    np.zeros(invrefvec.size - stpidx),
                )
            )
        else:
            self._invrefvec = invrefvec
        # A proper (power of 2) FFT size is selected, to accomodate the longest signal.
        # The recorded signal should be longer than the reference (swept-sine) one, but
        # it is tested which one is the longest, for safety.
        fftsze = 2 ** int(
            np.ceil(np.log2(self._refsglvec.size + self._recsglvec.size - 1))
        )  # Next power of 2
        # Get the inversed in time reference signal in the frequency domain.
        self._invrefspc = np.fft.fft(self._invrefvec, fftsze)
        # Get the recorder response signal in the frequency domain.
        self._recspc = np.fft.fft(
            (
                self._recsglvec
                if np.ndim(self._recsglvec) == 1
                else self._recsglvec[:, 0]
            ),  # Left channel by default
            fftsze,
        )
        # Get the reference swept-sine signal in the frequency domain.
        self._refspc = np.fft.fft(
            (
                self._refsglvec
                if np.ndim(self._refsglvec) == 1
                else self._refsglvec[:, 0]
            ),  # Left channel by default
            fftsze,
        )
        # Calculate the impulse response, by multiplying the recorder reponse signal
        # spectrum by the inversed in time reference swept-sine spectrum.
        self._irsspc = self._recspc * self._invrefspc
        # Get the impulse response in real time.
        irssglvec = np.fft.ifft(self._irsspc).real
        # Normalize the impulse response to sgllvl dB bellow its maximum absolut value.
        maxval = np.max(abs(irssglvec))
        irssglvec = irssglvec * 10 ** (self.sgllvl / 20) / maxval
        # Crop the impulse response signal, discarding the half first part and the
        # excess last part.
        irssglvec = irssglvec[self._refsglvec.size - 1 : 2 * self._refsglvec.size - 1]

        return (smprte, irssglvec)

    def save(self, /, path=None) -> None:
        """Create and save the impulse response signal in a WAV file.

        Parameters
        ----------
        path : string
            The filename path, for example "my_signal.wav" or
            "my_output/my_signal.wav". Default value is
            "./output/ss-signal.wav".

        """

        smprte, irssglvec = self.signal_vector()
        p = (
            Path("./" + _DEFAULT_OUTPUT_SUBFOLDER + "/" + _DEFAULT_IRSSIGNAL_FILENAME)
            if path is None
            else Path(path)
        )
        d = p.parent
        if not d.exists():
            d.mkdir(parents=True)
        sp.io.wavfile.write(p, smprte, irssglvec)


def main():
    """Execute the package from the command line"""

    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print(_USAGE_STRING)
        elif sys.argv[1] == "ss-save":
            signal = SweptSineSignal()
            if len(sys.argv) > 2:
                signal.save(sys.argv[2])
            else:
                print("Error: No filename path provided.")
                print("Run 'python -m scene_rir.rir --help' for usage.")
        elif sys.argv[1] == "ir-save":
            if len(sys.argv) >= 5:
                params = {
                    "rec_path": sys.argv[3],
                    "ref_path": sys.argv[4],
                }
                signal = ImpulseResponseSignal(params)
                signal.save(sys.argv[2])
            else:
                print("Error: No enough arguments provided.")
                print("Run 'python -m scene_rir.rir --help' for usage.")
        else:
            print(f'Error: unknown command "{sys.argv[1]}" for "scene_rir".')
            print("Run 'python -m scene_rir.rir --help' for usage.")
    else:
        print(_USAGE_STRING)


if __name__ == "__main__":
    main()
