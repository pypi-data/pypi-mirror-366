from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Vertical_Single(EpBunch):

    Name: Annotated[str, Field(default=...)]

    Ghe_Vertical_Properties_Object_Name: Annotated[str, Field(default=...)]

    X_Location: Annotated[float, Field(default=...)]

    Y_Location: Annotated[float, Field(default=...)]