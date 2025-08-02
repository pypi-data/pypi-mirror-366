from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontrol_Thermostat_Stageddualsetpoint(EpBunch):
    """Define the Thermostat StagedDualSetpoint settings for a zone or list of zones."""

    Name: Annotated[str, Field(default=...)]

    Zone_or_ZoneList_Name: Annotated[str, Field(default=...)]

    Number_of_Heating_Stages: Annotated[int, Field(default=..., ge=1, le=4)]
    """Enter the number of the following sets of data for heating temperature offset"""

    Heating_Temperature_Setpoint_Schedule_Name: Annotated[str, Field()]

    Heating_Throttling_Temperature_Range: Annotated[str, Field(default='1.1')]

    Stage_1_Heating_Temperature_Offset: Annotated[float, Field(default=..., le=0.0)]
    """The heating temperature offset is used to determine heating stage number for"""

    Stage_2_Heating_Temperature_Offset: Annotated[float, Field(le=0.0)]
    """The heating temperature offset is used to determine heating stage number for"""

    Stage_3_Heating_Temperature_Offset: Annotated[float, Field(le=0.0)]
    """The heating temperature offset is used to determine heating stage number for"""

    Stage_4_Heating_Temperature_Offset: Annotated[float, Field(le=0.0)]
    """The heating temperature offset is used to determine heating stage number for"""

    Number_of_Cooling_Stages: Annotated[int, Field(default=..., ge=1, le=4)]
    """Enter the number of the following sets of data for cooling temperature offset"""

    Cooling_Temperature_Setpoint_Base_Schedule_Name: Annotated[str, Field()]

    Cooling_Throttling_Temperature_Range: Annotated[str, Field(default='1.1')]

    Stage_1_Cooling_Temperature_Offset: Annotated[float, Field(default=..., ge=0.0)]
    """The cooling temperature offset is used to determine cooling stage number for"""

    Stage_2_Cooling_Temperature_Offset: Annotated[float, Field(ge=0.0)]
    """The cooling temperature offset is used to determine cooling stage number for"""

    Stage_3_Cooling_Temperature_Offset: Annotated[float, Field(ge=0.0)]
    """The cooling temperature offset is used to determine cooling stage number for"""

    Stage_4_Cooling_Temperature_Offset: Annotated[float, Field(ge=0.0)]
    """The cooling temperature offset is used to determine cooling stage number for"""