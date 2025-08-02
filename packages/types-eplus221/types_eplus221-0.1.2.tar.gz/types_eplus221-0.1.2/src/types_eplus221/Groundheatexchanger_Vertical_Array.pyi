from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Vertical_Array(EpBunch):

    Name: Annotated[str, Field(default=...)]

    GHEVerticalProperties_Object_Name: Annotated[str, Field(default=...)]

    Number_of_Boreholes_in_XDirection: Annotated[int, Field(default=..., ge=1)]

    Number_of_Boreholes_in_YDirection: Annotated[int, Field(default=..., ge=1)]

    Borehole_Spacing: Annotated[float, Field(default=..., gt=0.0)]