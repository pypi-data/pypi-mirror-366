from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Thermostat(EpBunch):
    """Zone thermostat control. Referenced schedules must be"""

    Name: Annotated[str, Field(default=...)]
    """This name is referenced by HVACTemplate:Zone:* objects"""

    Heating_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint specified below, must enter schedule or constant setpoint"""

    Constant_Heating_Setpoint: Annotated[str, Field()]
    """Ignored if schedule specified above, must enter schedule or constant setpoint"""

    Cooling_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint specified below, must enter schedule or constant setpoint"""

    Constant_Cooling_Setpoint: Annotated[str, Field()]
    """Ignored if schedule specified above, must enter schedule or constant setpoint"""