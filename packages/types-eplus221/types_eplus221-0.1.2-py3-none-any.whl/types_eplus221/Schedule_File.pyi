from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_File(EpBunch):
    """A Schedule:File points to a text computer file that has 8760-8784 hours of data."""

    Name: Annotated[str, Field(default=...)]

    Schedule_Type_Limits_Name: Annotated[str, Field()]

    File_Name: Annotated[str, Field(default=...)]

    Column_Number: Annotated[int, Field(default=..., ge=1)]

    Rows_to_Skip_at_Top: Annotated[int, Field(default=..., ge=0)]

    Number_of_Hours_of_Data: Annotated[str, Field(default='8760')]
    """8760 hours does not account for leap years, 8784 does."""

    Column_Separator: Annotated[Literal['Comma', 'Tab', 'Space', 'Semicolon'], Field(default='Comma')]

    Interpolate_to_Timestep: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """when the interval does not match the user specified timestep a "Yes" choice will average between the intervals request (to"""

    Minutes_per_Item: Annotated[int, Field(ge=1, le=60)]
    """Must be evenly divisible into 60"""