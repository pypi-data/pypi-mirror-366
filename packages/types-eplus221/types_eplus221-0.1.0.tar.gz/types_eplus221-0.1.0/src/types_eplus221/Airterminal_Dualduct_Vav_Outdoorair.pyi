from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Dualduct_Vav_Outdoorair(EpBunch):
    """Central air system terminal unit, dual duct, variable volume with special controls."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The outlet node of the terminal unit."""

    Outdoor_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Recirculated_Air_Inlet_Node_Name: Annotated[str, Field()]

    Maximum_Terminal_Air_Flow_Rate: Annotated[str, Field(default=...)]
    """If autosized this is the sum of flow needed for cooling and maximum required outdoor air"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field(default=...)]
    """When the name of a DesignSpecification:OutdoorAir object is entered, the terminal"""

    Per_Person_Ventilation_Rate_Mode: Annotated[Literal['CurrentOccupancy', 'DesignOccupancy'], Field()]
    """CurrentOccupancy models demand controlled ventilation using the current number of people"""