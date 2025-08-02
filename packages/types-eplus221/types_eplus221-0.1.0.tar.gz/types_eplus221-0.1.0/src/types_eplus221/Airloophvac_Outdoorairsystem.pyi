from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Outdoorairsystem(EpBunch):
    """Outdoor air subsystem for an AirLoopHVAC. Includes an outdoor air mixing box and"""

    Name: Annotated[str, Field(default=...)]

    Controller_List_Name: Annotated[str, Field()]
    """Enter the name of an AirLoopHVAC:ControllerList object or blank if this object is used in"""

    Outdoor_Air_Equipment_List_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirLoopHVAC:OutdoorAirSystem:EquipmentList object."""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""