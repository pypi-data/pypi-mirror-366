from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_Constant(EpBunch):
    """Constant hourly value for entire year."""

    Name: Annotated[str, Field(default=...)]

    Schedule_Type_Limits_Name: Annotated[str, Field()]

    Hourly_Value: Annotated[float, Field(default=0)]