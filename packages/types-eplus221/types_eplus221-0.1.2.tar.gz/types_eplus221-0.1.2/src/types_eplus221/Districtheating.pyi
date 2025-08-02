from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Districtheating(EpBunch):
    """Centralized source of hot water, such as a district heating system."""

    Name: Annotated[str, Field(default=...)]

    Hot_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Hot_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Nominal_Capacity: Annotated[str, Field()]

    Capacity_Fraction_Schedule_Name: Annotated[str, Field()]
    """Schedule values are multiplied by Nominal Capacity for current capacity"""