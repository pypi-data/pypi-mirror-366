from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Vav_Heatandcool_Noreheat(EpBunch):
    """Central air system terminal unit, single duct, variable volume for both cooling and"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The outlet node of the terminal unit."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Maximum_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Zone_Minimum_Air_Flow_Fraction: Annotated[str, Field(default=...)]
    """fraction of maximum air flow"""