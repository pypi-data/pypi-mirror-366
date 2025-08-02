from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Dualduct_Constantvolume(EpBunch):
    """Central air system terminal unit, dual duct, constant volume."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The outlet node of the terminal unit."""

    Hot_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Cold_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Maximum_Air_Flow_Rate: Annotated[str, Field(default=...)]