from pydantic import PrivateAttr

from .common import ConstantWaveform, Experiment


class ReadoutClassifierCalibration(Experiment):
    """
    Parameters for running calibration of readout classifier for a transmon.

    Parameters
    ----------
    transmon : str
        The reference for the transmon to target in the experiment.
    recycle_delay_ns : int
        The delay time between consecutive shots of the experiment, in nanoseconds.
    shot_count : int, optional
        The number of shots to be taken in the experiment.
        Defaults to 5000.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        If not provided, the measurement defcal will be used.
    """

    _experiment_name: str = PrivateAttr("readout_classifier_calibration")
    transmon: str
    recycle_delay_ns: int
    shot_count: int = 5000
    measure_waveform: ConstantWaveform | None = None
