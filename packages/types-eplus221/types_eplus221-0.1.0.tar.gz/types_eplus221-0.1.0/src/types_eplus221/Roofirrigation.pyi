from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roofirrigation(EpBunch):
    """Used to describe the amount of irrigation on the ecoroof surface over the course"""

    Irrigation_Model_Type: Annotated[Literal['Schedule', 'SmartSchedule'], Field()]
    """SmartSchedule will not allow irrigation when soil is already moist."""

    Irrigation_Rate_Schedule_Name: Annotated[str, Field()]
    """Schedule values in meters of water per hour"""

    Irrigation_Maximum_Saturation_Threshold: Annotated[str, Field(default='40.0')]
    """Used with SmartSchedule to set the saturation level at which no"""