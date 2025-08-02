from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermostatsetpoint_Thermalcomfort_Fanger_Dualsetpoint(EpBunch):
    """Used for heating and cooling thermal comfort control with dual setpoints. The PMV"""

    Name: Annotated[str, Field(default=...)]

    Fanger_Thermal_Comfort_Heating_Schedule_Name: Annotated[str, Field(default=...)]
    """Schedule values should be Predicted Mean Vote (PMV)"""

    Fanger_Thermal_Comfort_Cooling_Schedule_Name: Annotated[str, Field(default=...)]
    """Schedule values should be Predicted Mean Vote (PMV)"""