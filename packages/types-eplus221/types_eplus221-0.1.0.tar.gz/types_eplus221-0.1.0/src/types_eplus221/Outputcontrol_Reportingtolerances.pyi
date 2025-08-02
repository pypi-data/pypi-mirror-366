from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Outputcontrol_Reportingtolerances(EpBunch):
    """Calculations of the time that setpoints are not met use a tolerance of 0.2C."""

    Tolerance_For_Time_Heating_Setpoint_Not_Met: Annotated[str, Field(default='.2')]
    """If the zone temperature is below the heating setpoint by more than"""

    Tolerance_For_Time_Cooling_Setpoint_Not_Met: Annotated[str, Field(default='.2')]
    """If the zone temperature is above the cooling setpoint by more than"""