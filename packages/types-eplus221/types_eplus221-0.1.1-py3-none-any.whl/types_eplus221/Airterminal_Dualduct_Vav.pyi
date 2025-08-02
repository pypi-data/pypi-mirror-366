from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Dualduct_Vav(EpBunch):
    """Central air system terminal unit, dual duct, variable volume."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The outlet node of the terminal unit."""

    Hot_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Cold_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Maximum_Damper_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Zone_Minimum_Air_Flow_Fraction: Annotated[str, Field(default='0.2')]
    """fraction of maximum air flow"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """When the name of a DesignSpecification:OutdoorAir object is entered, the terminal"""