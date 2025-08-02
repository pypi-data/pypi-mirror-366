from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Vertical_Single(EpBunch):

    Name: Annotated[str, Field(default=...)]

    GHEVerticalProperties_Object_Name: Annotated[str, Field(default=...)]

    XLocation: Annotated[float, Field(default=...)]

    YLocation: Annotated[float, Field(default=...)]