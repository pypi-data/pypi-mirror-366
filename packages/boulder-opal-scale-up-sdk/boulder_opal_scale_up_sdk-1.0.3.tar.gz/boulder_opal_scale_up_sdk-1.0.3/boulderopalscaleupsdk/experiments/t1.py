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

from .common import Experiment, LogspaceIterable

DEFAULT_RECYCLE_DELAY_NS = 200_000
DEFAULT_SHOT_COUNT = 400
DEFAULT_DURATION_NS = 2_000


class T1(Experiment):
    """
    Parameters for running a T1 experiment.

    Parameters
    ----------
    transmon : str
        The transmon to target in the experiment.
    delays_ns : list[int] | RangeIterable
        The delay time, in nanoseconds.
    readout_amplitude : float, optional
        The amplitude of the readout pulse.
        If None, a default amplitude will be used.
    duration_ns : int, optional
        The duration of the readout pulse, in nanoseconds.
        Defaults to 2000 ns.
    recycle_delay_ns : int, optional
        The delay time between consecutive shots of the experiment, in nanoseconds.
        Defaults to 200_000 ns.
    shot_count : int, optional
        The number of shots to be taken in the experiment.
        Defaults to 400.
    """

    _experiment_name: str = PrivateAttr("t1")

    transmon: str
    delays_ns: LogspaceIterable
    readout_amplitude: float
    duration_ns: int = DEFAULT_DURATION_NS
    recycle_delay_ns: int = DEFAULT_RECYCLE_DELAY_NS
    shot_count: int = DEFAULT_SHOT_COUNT
