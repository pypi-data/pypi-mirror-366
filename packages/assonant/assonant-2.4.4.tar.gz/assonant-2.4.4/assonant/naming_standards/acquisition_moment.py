from enum import Enum


class AcquisitionMoment(Enum):
    """Possible Acquisition Moment values."""

    START = "Start"
    DURING = "During"
    END = "End"
