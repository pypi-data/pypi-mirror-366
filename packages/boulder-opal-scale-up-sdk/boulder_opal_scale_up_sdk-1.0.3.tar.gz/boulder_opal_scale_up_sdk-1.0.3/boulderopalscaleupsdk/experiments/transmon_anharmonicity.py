# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from pydantic import PrivateAttr

from .common import (
    ConstantWaveform,
    CWSIterable,
    Experiment,
    HypIterable,
    LinspaceIterable,
    RangeIterable,
)

DEFAULT_DURATION_NS = 2_000  # ns
DEFAULT_RECYCLE_DELAY_NS = 1_000  # ns
DEFAULT_SHOT_COUNT = 100
DEFAULT_ANHARMONICITY_GUESS = -200e6  # Hz, typical anharmonicity for transmons


class TransmonAnharmonicity(Experiment):
    """
    Parameters for running a Qubit Anharmonicity experiment.

    Parameters
    ----------
    transmon : str
        The transmon that is the target of the experiment.
    frequencies : list[int] or LinspaceIterable or RangeIterable or CWSIterable
                  or HypIterable or None, optional
        The drive frequencies to be scanned in the experiment.
        If None, a default scan will be used based on the transmon's frequency
        and anharmonicity.
    anharmonicity_guess_hz : float
        The guessed anharmonicity of the qubit, in Hz. This is used to determine the
        range of frequencies to scan if `frequencies` is not provided.
        Defaults to -200 MHz.
    recycle_delay_ns : int, optional
        The delay time between consecutive shots of the experiment, in nanoseconds.
        Defaults to 1000 ns.
    shot_count : int, optional
        The number of shots to be taken in the experiment. Defaults to 100.
    spectroscopy_waveform : ConstantWaveform or None, optional
        The waveform to use in the spectroscopy pulse.
        If not provided, a waveform with a duration of 2000 ns
        and an amplitude of 1.5 times the transmon's x_vp will be used.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        If not provided, the measurement defcal will be used.
    """

    _experiment_name: str = PrivateAttr("transmon_anharmonicity")

    transmon: str
    frequencies: list[int] | LinspaceIterable | RangeIterable | CWSIterable | HypIterable | None = (
        None
    )
    anharmonicity_guess_hz: float = DEFAULT_ANHARMONICITY_GUESS
    recycle_delay_ns: int = DEFAULT_RECYCLE_DELAY_NS
    shot_count: int = DEFAULT_SHOT_COUNT
    spectroscopy_waveform: ConstantWaveform | None = None
    measure_waveform: ConstantWaveform | None = None
