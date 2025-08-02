from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Zonecontrol_Pressurecontroller(EpBunch):
    """This object is used to control a zone to a specified indoor pressure"""

    Name: Annotated[str, Field(default=...)]

    Control_Zone_Name: Annotated[str, Field(default=...)]

    Control_Object_Type: Annotated[Literal['AirflowNetwork:MultiZone:Component:ZoneExhaustFan', 'AirflowNetwork:Distribution:Component:ReliefAirFlow'], Field(default=...)]
    """The current selection is AirflowNetwork:MultiZone:Component:ZoneExhaustFan"""

    Control_Object_Name: Annotated[str, Field(default=...)]
    """Control names are names of individual control objects"""

    Pressure_Control_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for pressure controller. Schedule value > 0 means the"""

    Pressure_Setpoint_Schedule_Name: Annotated[str, Field(default=...)]