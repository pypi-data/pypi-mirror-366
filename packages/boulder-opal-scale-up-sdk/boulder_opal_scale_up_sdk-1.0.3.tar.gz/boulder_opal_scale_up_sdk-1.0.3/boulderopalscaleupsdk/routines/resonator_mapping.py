from pydantic import PrivateAttr

from boulderopalscaleupsdk.routines import Routine


class ResonatorMapping(Routine):
    """
    Parameters for running a resonator mapping routine.

    Parameters
    ----------
    feedlines : list[str] or None
        The feedlines to target in the routine.
        If not provided, all feedlines in the device will be targeted.
    """

    _routine_name: str = PrivateAttr("resonator_mapping")

    feedlines: list[str] | None = None
