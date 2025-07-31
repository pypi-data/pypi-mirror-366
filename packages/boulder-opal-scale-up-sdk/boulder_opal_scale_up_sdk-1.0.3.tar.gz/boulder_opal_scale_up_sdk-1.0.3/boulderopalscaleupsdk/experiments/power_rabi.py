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
    GaussianWaveform,
    HypIterable,
    LinspaceIterable,
    RangeIterable,
)

DEFAULT_SHOT_COUNT = 400


class PowerRabi(Experiment):
    """
    Parameters for running a Power Rabi experiment.

    Parameters
    ----------
    transmon : str
        The reference for the transmon to target in the experiment.
    scales : list[float] or LinspaceIterable or RangeIterable
            or CWSIterable or HypIterable or None, optional
        The scaling factors for the drive pulse amplitude. If None, a default scan will be used.
    drive_waveform : GaussianWaveform
        The waveform to use for the drive pulse.
    recycle_delay_ns : int
        The delay time between consecutive shots of the experiment, in nanoseconds.
    shot_count : int, optional
        The number of shots to be taken in the experiment. Defaults to 400.
    pulse_vp : float, optional
        The voltage per pulse. If None, a default value will be used.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        If not provided, the measurement defcal will be used.
    """

    _experiment_name: str = PrivateAttr("power_rabi")

    transmon: str
    scales: list[float] | LinspaceIterable | RangeIterable | CWSIterable | HypIterable | None = None
    drive_waveform: GaussianWaveform
    recycle_delay_ns: int
    shot_count: int = DEFAULT_SHOT_COUNT
    pulse_vp: float | None = None
    measure_waveform: ConstantWaveform | None = None
