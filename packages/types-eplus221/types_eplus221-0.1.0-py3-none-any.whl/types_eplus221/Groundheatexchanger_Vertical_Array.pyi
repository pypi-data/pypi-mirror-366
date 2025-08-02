from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Vertical_Array(EpBunch):

    Name: Annotated[str, Field(default=...)]

    Ghe_Vertical_Properties_Object_Name: Annotated[str, Field(default=...)]

    Number_Of_Boreholes_In_X_Direction: Annotated[int, Field(default=..., ge=1)]

    Number_Of_Boreholes_In_Y_Direction: Annotated[int, Field(default=..., ge=1)]

    Borehole_Spacing: Annotated[float, Field(default=..., gt=0.0)]