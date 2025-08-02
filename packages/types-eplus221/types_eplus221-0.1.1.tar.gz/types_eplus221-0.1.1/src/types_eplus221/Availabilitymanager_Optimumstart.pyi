from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Availabilitymanager_Optimumstart(EpBunch):
    """Determines the optimal start of HVAC systems before occupancy."""

    Name: Annotated[str, Field(default=...)]

    Applicability_Schedule_Name: Annotated[str, Field(default=...)]

    Fan_Schedule_Name: Annotated[str, Field(default=...)]

    Control_Type: Annotated[Literal['StayOff', 'ControlZone', 'MaximumofZoneList'], Field(default='ControlZone')]

    Control_Zone_Name: Annotated[str, Field()]

    Zone_List_Name: Annotated[str, Field()]

    Maximum_Value_For_Optimum_Start_Time: Annotated[str, Field(default='6')]
    """this is the maximum number of hours that a system can start before occupancy"""

    Control_Algorithm: Annotated[Literal['ConstantTemperatureGradient', 'AdaptiveTemperatureGradient', 'AdaptiveASHRAE', 'ConstantStartTime'], Field(default='AdaptiveASHRAE')]

    Constant_Temperature_Gradient_During_Cooling: Annotated[float, Field()]

    Constant_Temperature_Gradient_During_Heating: Annotated[float, Field()]

    Initial_Temperature_Gradient_During_Cooling: Annotated[float, Field()]

    Initial_Temperature_Gradient_During_Heating: Annotated[float, Field()]

    Constant_Start_Time: Annotated[float, Field()]
    """this is the number of hours before occupancy for a system"""

    Number_Of_Previous_Days: Annotated[int, Field(ge=2, le=5, default=2)]
    """this is the number of days that their actual temperature"""