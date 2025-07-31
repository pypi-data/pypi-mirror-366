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

DEFAULT_DURATION_NS = 2000  # ns
DEFAULT_RECYCLE_DELAY_NS = 1000  # ns
DEFAULT_SHOT_COUNT = 100


class ResonatorSpectroscopy(Experiment):
    """
    Parameters for running a resonator spectroscopy experiment.

    Parameters
    ----------
    resonator : str
        The reference for the resonator to target in the experiment.
    frequencies : list[int] or LinspaceIterable or RangeIterable or CWSIterable
                  or HypIterable or None, optional
        The frequencies at which to scan.
        If None, frequencies around the readout frequency will be used.
    recycle_delay_ns :int, optional
        The delay time between consecutive shots of the experiment, in nanoseconds.
        Defaults to 1000 ns.
    shot_count : int, optional
        The number of shots to be taken in the experiment.
        Defaults to 100.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        If not provided, the measurement defcal will be used.
    """

    _experiment_name: str = PrivateAttr("resonator_spectroscopy")

    resonator: str
    frequencies: list[int] | LinspaceIterable | RangeIterable | CWSIterable | HypIterable | None = (
        None
    )
    recycle_delay_ns: int = DEFAULT_RECYCLE_DELAY_NS
    shot_count: int = DEFAULT_SHOT_COUNT
    measure_waveform: ConstantWaveform | None = None
