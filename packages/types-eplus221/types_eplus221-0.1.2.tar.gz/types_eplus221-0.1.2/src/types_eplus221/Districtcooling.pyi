from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Districtcooling(EpBunch):
    """Centralized source of chilled water, such as a district cooling system."""

    Name: Annotated[str, Field(default=...)]

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Nominal_Capacity: Annotated[str, Field()]

    Capacity_Fraction_Schedule_Name: Annotated[str, Field()]
    """Schedule values are multiplied by Nominal Capacity for current capacity"""